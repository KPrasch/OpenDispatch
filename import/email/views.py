from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datetime import datetime, timedelta
from dispatch.models import UlsterIncident
from dispatch_gmail.models import IncidentEmail
import getpass, os, email, sys, gmail, dispatch_gmail, re, time, imaplib, string, pywapi
import pdb
from chartit import DataPool, Chart
import json as simplejson
from collections import Counter
import operator
from dispatch.models import *
from dispatch.views import get_coordinates
from dispatch.views import parse_incident


def import_email_incidents(request):
    '''
    This view connects to an individuals gmail inbox, selects emails sent from 911 Dispatch,
    by sender address, and saves the emails to the databsse.
    '''
    usernm = raw_input("Username:")
    passwd = getpass.getpass(prompt='Password: ', stream=None)
    conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    conn.login(usernm,passwd)
    conn.select('Dispatch')

    #Only trying to parse the emails that are relevant. Selecting by sender and subject.
    typ, data = conn.search(None, '(FROM "messaging@iamresponding.com" SUBJECT "Company 43")')
    
    #Extract the data we need.
    for num in data[0].split():
        typ, msg_data = conn.fetch(num, '(RFC822)')
        for response_part in msg_data:
              if isinstance(response_part,tuple):
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
                  parse_incident(payload, received_datetime)
    print "Done."
    #return '\n'.join([get_incident_emails(part.get_payload()) for part in payload])
    return render(request, 'dashboard.html')
    #return redirect('parse_incident_emails')
