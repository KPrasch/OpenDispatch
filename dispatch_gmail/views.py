from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datetime import datetime
from dispatch_gmail.models import IncidentEmail, Incident
import getpass, os, email, sys, gmail, dispatch_gmail, re, time, imaplib, string, pywapi
import pdb


def gross_hourly_chart(request):

    incident_list = IncidentEmail.objects.all()
    for incidentemail in incident_list:
        datetime_str = incidentemail.datetime_str
        #Step 1: Create a DataPool with the data we want to retrieve.
        incidentdata = \
            DataPool(
               series=
                [{'options': {
                   'source': GrossHourlyIncidents.objects.all()},
                  'terms': [
                    'hour',
                    'count',]}
                 ])

        #Step 2: Create the Chart object
        cht = Chart(
                datasource = incidentdata,
                series_options =
                  [{'options':{
                      'type': 'line',
                      'stacking': False},
                    'terms':{
                      'hour': [
                        'count',]
                      }}],
                chart_options =
                  {'title': {
                       'text': 'All Incident Occurances by Hour'},
                   'xAxis': {
                        'title': {
                           'text': 'Time'}}})

    #Step 3: Send the chart object to the template.
    return render(request, 'dashboard.html', {'grosshourchart': cht})


def incident_table(request):

    incident_list = Incident.objects.all()
    context = {'incident_list': incident_list}
    return render(request, 'dashboard.html', context)


def parse_incident_emails(request):

    total = IncidentEmail.objects.all().count()
    print ("Total Email Incidents:", total)
    incident_email_list = IncidentEmail.objects.all()
    for i in incident_email_list:
      body = i.payload
      sent = i.datetime_str
      #pdb.set_trace()
      date = datetime.strptime(sent, '%d %b %Y %H:%M:%S -0700' )
      # Create a set of target strings, and craete a regular expressions pattern to select the text between them.
      keys = set(('Inc', 'Nature', 'XSts', 'Common', 'Addtl', 'Loc', 'Date', 'Time'))
      key_re = re.compile('(' + '|'.join(re.escape(key) for key in keys) + '):', re.IGNORECASE)
      key_locations = key_re.split(body)[1:]
      incident_dict = {k: v.strip() for k,v in zip(key_locations[::2], key_locations[1::2])}
      # Create a model instance for each incident.
      incident = Incident.objects.create(datetime_str = date, **incident_dict)
      # Save the Incident to the database.
      incident.save()
      print "Successfuly created incident # %s:%s." % (incident.id, incident.Inc)
    return render(request, 'dashboard.html')


def get_incident_emails(request):
    '''
    This view connects to an individuals gmail inbox, selects emails sent from 911 Dispatch,
    by sender address, and saves the emails to the databsse.
    '''
    usernm = raw_input("Username:")
    passwd = getpass.getpass(prompt='Password: ', stream=None)
    conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    conn.login(usernm,passwd)

    # Selecting by Gmail Label 'Dispatch' like It's an IMAP folder.
    print("Total Incidents Found:", conn.select('Dispatch'))

    # Only trying to parse the emails that are relevant. Selecting by sender and subject.
    typ, data = conn.search(None, '(FROM "messaging@iamresponding.com" SUBJECT "Company 43")')
    for num in data[0].split():
        typ, msg_data = conn.fetch(num, '(RFC822)')
        for response_part in msg_data:
              if isinstance(response_part,tuple):
                  msg = email.message_from_string(response_part[1])
                  payload = msg.get_payload(decode=True)
                  #pdb.set_trace()
                  email_fields_dict = {'datetime_str':msg["Date"],'payload':payload}
                  incident_email = IncidentEmail.objects.create(**email_fields_dict)
                  incident_email.save()
                  print "Saved email #%s" % incident_email.id

    #return '\n'.join([get_incident_emails(part.get_payload()) for part in payload])
    return render(request, 'dashboard.html', locals())
