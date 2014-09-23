from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext

import getpass, os, email, sys, gmail, dispatch_gmail, re, time, imaplib

from dispatch_gmail.models import *


def dashboard(request):
    incident_list = Incident.objects.all()
    context = {'incident_list': incident_list}
    return render(request, 'dashboard.html', context)



'''
def extracation_status(payload):
  if isinstance(payload,str):
      return render_to_response('index.html', incident_dict)
  else:
      return '\n'.join([extract_gmail_incidents(part.get_payload()) for part in payload])

def extract_gmail_incidents(request, payload):

    This function connects to an individuals gmail inbox, selects emails sent from 911 Dispatch,
    by sender address, and parses dispatch data into one dictionary per incident.

    The dictionary is passed to the Incident model and creates instances.


    if isinstance(payload,str):
        return render_to_response('index.html', incident_dict)
    else:
        return '\n'.join([extract_gmail_incidents(part.get_payload()) for part in payload])

#extracation_status(payload)
# Connect and Authenticate Gmail account.  This is happening in the Terminal for now.
# Need Frontend / Gmail API Integration here
usernm = raw_input("Username:")
passwd = getpass.getpass(prompt='Password: ', stream=None)
conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
conn.login(usernm,passwd)

# Selecting by Gmail Label 'Dispatch' like It's an IMAP folder.
print("Total Incidents Found:", conn.select('Dispatch'))
# Only trying to parse the emails that are relevant. Selecting by sender and subject.
typ, data = conn.search(None, '(FROM "messaging@iamresponding.com" SUBJECT "Company 43")')

# Create a set of target strings, and craete a regular expressions pattern to select the text between them.
keys = set(('Inc', 'Nature', 'XSts', 'Common', 'Addtl', 'Loc', 'Date', 'Time'))
key_re = re.compile('(' + '|'.join(re.escape(key) for key in keys) + '):', re.IGNORECASE)

try:
    for num in data[0].split():
        typ, msg_data = conn.fetch(num, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part,tuple):
                msg = email.message_from_string(response_part[1])
                payload = msg.get_payload()
                body = extract_gmail_incidents(payload)
                try:
                  # Extract the incident text data with regular expressions and create a dictionary for each incident.
                  sent = msg["Date"]
                  key_locations = key_re.split(body)[1:]
                  incident_dict = {k: v.strip() for k,v in zip(key_locations[::2], key_locations[1::2])}
                  # Create a model instance for each incident.
                  incident = Incident.objects.create(recieved = sent, **incident_dict)
                  # Save the Incident to the database.
                  incident.save()
                  print "Successfuly created incident # %s:%s." % (incident.id, incident.Inc)
                except IndexError:
                  print "malformed incident email."

#close the connection and logout.
finally:
    try:
        conn.close()
    except:
        pass
    conn.logout()





def incident_table(request):


  return render_to_response('index.html', incident_dict)
'''
