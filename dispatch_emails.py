# -*- coding: utf-8 -*-
import getpass, os, imaplib, email, sys


def extract_gmail_dispatches(payload):
    if isinstance(payload,str):
        return payload
    else:
        return '\n'.join([extract_gmail_dispatches(part.get_payload()) for part in payload])

# Connect and Authenticate.
usernm = raw_input("Username:")
passwd = getpass.getpass(prompt='Password: ', stream=None)
conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
conn.login(usernm,passwd)

# Selecting by Gmail Labels like they are IMAP folders
# Terminal output for debugging
print("Total of", conn.select('Dispatch'), "dispatches found.")

fields =  ['Unit', 'Inc', 'Venue', 'Nature', 'Xsts', 'Loc', 'Common', 'Addtl']


#Only trying to parse the emails that are relevant. Selecting by sender and subject - NO Gmail labels here.
typ, data = conn.search(None, '(FROM "messaging@iamresponding.com" SUBJECT "Company 43")')
try:
    for num in data[0].split():
        typ, msg_data = conn.fetch(num, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_string(response_part[1])
                subject=msg['subject']
                # Just print the subject for now
                print(subject)

                payload=msg.get_payload()
                body=extract_gmail_dispatches(payload)
                # Just print the email body for now
                print(body)

        #Mark the message as read in Gmail
        typ, response = conn.store(num, '+FLAGS', r'(\Seen)')

#close the connection and logout.
finally:
    try:
        conn.close()
    except:
        pass
    conn.logout()
