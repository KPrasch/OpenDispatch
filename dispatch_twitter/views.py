from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datetime import datetime, timedelta
from dispatch_gmail.models import IncidentEmail
from dispatch.models import UlsterIncident
import getpass, os, email, sys, gmail, dispatch_gmail, re, time, imaplib, string, pywapi
import pdb
from chartit import DataPool, Chart
import json as simplejson
from collections import Counter
import operator


def get_twitter_incidents(request):
    '''
    This view connects to an individuals gmail inbox, selects emails sent from 911 Dispatch,
    by sender address, and saves the emails to the databsse.
    '''
    usernm = raw_input("Username:")
    passwd = getpass.getpass(prompt='Password: ', stream=None)
    conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    conn.login(usernm,passwd)
    conn.select('Dispatch')
    
    msg = email.message_from_string(response_part[1])
    time_stamp = email.utils.parsedate(msg['Date'])
    time_int = time.mktime(time_stamp)
    received_datetime = datetime.fromtimestamp(time_int)
    payload = msg.get_payload(decode=True)
    #pdb.set_trace()
    incident_email = IncidentEmail.objects.create(datetime = received_datetime, payload = payload)
    incident_email.save()
    sys.stdout.write("Saved email #%s \r" % incident_email.id)
    sys.stdout.flush()

    print "Done."
    #return '\n'.join([get_incident_emails(part.get_payload()) for part in payload])
    return render(request, 'dashboard.html')
    #return redirect('parse_incident_emails')

def parse_twitter_incidents(request):

    total = IncidentEmail.objects.all().count()
    print ("Total Email Incidents in db:", total)
    incident_email_list = IncidentEmail.objects.all()
    for incident in incident_email_list:
      body = incident.payload
      sent = incident.datetime
      # Create a set of target strings, and craete a regular expressions pattern to select the text between them.
      keys = set(('Unit', 'Venue', 'Inc', 'Nature', 'XSts', 'Common', 'Addtl', 'Loc', 'Date', 'Time'))
      key_re = re.compile('(' + '|'.join(re.escape(key) for key in keys) + '):', re.IGNORECASE)
      key_locations = key_re.split(body)[1:]
      incident_dict = {k: v.strip() for k,v in zip(key_locations[::2], key_locations[1::2])}
      #pdb.set_trace()
      
      # Create a model instance for each incident.
      incident = Incident.objects.create(payload = body, datetime = sent, **incident_dict)
      # Save the Incident to the database.
      incident.save()
      sys.stdout.write("Successfuly created incident # %s:%s \r." % (incident.id, incident.Inc))
      sys.stdout.flush()
    print "Done."

    return render(request, 'dashboard.html')
