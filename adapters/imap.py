

def fetch_imap_incidents(request, username):
    """
    This view connects to an individuals gmail inbox, selects emails sent from 911 Dispatch,
    by sender address, and saves the emails to the database.
    """
    usernm = input("Username:")
    passwd = getpass.getpass(prompt='Password: ', stream=None)
    conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    conn.login(usernm, passwd)
    conn.select('Dispatch')

    # Only trying to parse the emails that are relevant. Selecting by sender and subject.
    typ, data = conn.search(None, '(FROM "messaging@iamresponding.com" SUBJECT "Company 43")')

    # Extract the data we need.
    for num in data[0].split():
        typ, msg_data = conn.fetch(num, '(RFC822)')
        for response_part in msg_data:

            if isinstance(response_part, tuple):
                msg = email.message_from_string(response_part[1])
                time_stamp = email.utils.parsedate(msg['Date'])
                time_int = time.mktime(time_stamp)
                received_datetime = datetime.fromtimestamp(time_int)
                payload = msg.get_payload(decode=True)
                process_import(payload, received_datetime)

    return HttpResponse(status=201)