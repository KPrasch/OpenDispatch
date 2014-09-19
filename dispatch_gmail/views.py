from django.shortcuts import render
from django.http import HttpResponse

import getpass, os, imaplib, email, sys, gmail, dispatch_gmail, re

from dispatch_gmail import models

def extract_gmail_iar_incidents(payload):
    if isinstance(payload,str):
        return payload
    else:
        return '\n'.join([extract_gmail_iar_incidents(part.get_payload()) for part in payload])

# Connect and Authenticate Gmail account.  This is happening in the Terminal for now.
usernm = raw_input("Username:")
passwd = getpass.getpass(prompt='Password: ', stream=None)
conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
conn.login(usernm,passwd)

# Selecting by Gmail Label 'Dispatch' like It's an IMAP folder - Terminal output.
print("Total Incidents Found:", conn.select('Dispatch'))

keys = set(('Inc', 'Nature', 'XSts', 'Common', 'Addtl', 'NotAKey'))
key_re = re.compile('(' + '|'.join(re.escape(key) for key in keys) + '):', re.IGNORECASE)

#Only trying to parse the emails that are relevant. Selecting by sender and subject - NO Gmail labels here.
typ, data = conn.search(None, '(FROM "messaging@iamresponding.com" SUBJECT "Company 43")')
try:
    for num in data[0].split():
        typ, msg_data = conn.fetch(num, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part,tuple):
                msg = email.message_from_string(response_part[1])
                payload = msg.get_payload()
                body = extract_gmail_iar_incidents(payload)
                # Extraxt the incident text data with regular expressions.
                try:
                  key_locations = key_re.split(body)[1:]
                  print {k: v.strip() for k,v in zip(key_locations[::2], key_locations[1::2])}
                except IndexError:
                  print "No matches found."

                # Create a model instance
                #incident = Incident.objects.create_incident(incident_data)

#close the connection and logout.
finally:
    try:
        conn.close()
    except:
        pass
    conn.logout()
