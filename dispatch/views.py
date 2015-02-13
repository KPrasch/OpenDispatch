from collections import Counter
from datetime import datetime, timedelta
import getpass, os, email, sys, gmail, dispatch_gmail, re, time, imaplib, string, pywapi
import operator
import pdb
import urllib

from chartit import DataPool, Chart
from dispatch.models import UlsterIncident
from dispatch_gmail.models import IncidentEmail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import json as simplejson
import simplejson
import dispatch_settings


def import_incidents(source):
    '''
    '''
    if source == 'twitter':
      raw_incident = get_twitter_incidents(dispatch_settings.TWITTER_USERNAME)
    elif source == 'email':
      raw_incident = import_email_incidents(dispatch_settings.EMAIL_USERNAME)
    else:
      return ValueError("Invalid dispatch source.  Please specify twitter, email or cad.")  
      
    normalized_data = normalize_incidnt_data(raw_incident.payload)
    parse = parse_incident(normalized_data.payload, raw_incident.recieved_datetime)
    incident_dict = parse.incident_dict
    geocode = geocode_incident(incident_dict)
    incident = UlsterIncident.objects.create(datetime = raw_incident.recieved_datetime, lat = geocode[0], long = geocode[1], **incident_dict)
    incident.save()
    print "Created Incident %d" % incident.id

    return HttpResponse('200')

def get_current_weather(request):
    pass

def get_historical_weather(request):
    pass

def normalize_incidnt_data(payload):
    '''
    Converts unicode data to a python string.
    '''
    decoded_payload =  unicodedata.normalize('NFKD', payload).encode('ascii', 'ignore') 
    payload = decoded_payload.replace('\n', '').replace('\r', '')
    return payload
    
def parse_incident(payload, sent):
    '''
    Using configurable incident data fields, parse the data into incident models with all of the information required.
    '''
    keys = set(dispatch_settings.INCIDENT_FIELDS)
    key_re = re.compile('(' + '|'.join(re.escape(key) for key in keys) + ')%r' % dispatch_settings.DELINIATER, re.IGNORECASE)
    key_locations = key_re.split(payload)[1:]
    incident_dict = {k: v.strip() for k,v in zip(key_locations[::2], key_locations[1::2])}
    # Create a model instance for each incident.
    return incident_dict

def get_coordinates(incident_dict, from_sensor=False):
    '''
    Uses the unauthenticated Google Maps API V3.  using passed incident dictionary,
    gather relevant location text and return a latitude and logitude for an incident. 
    '''
    googleGeocodeUrl = 'http://maps.googleapis.com/maps/api/geocode/json?'
    location_fields = dispatch_settings.LOCATION_FIELDS
    incident_location_data = [incident_dict[x] for x in location_fields]
    incident_location_data = " ".join(incident_location_data).LOWER  + dispatch_settings.LOCALE_STATE
    
    #Back to unicode
    incident_location_data = incident_location_data.encode('utf-8')
    params = {
        'address': incident_location_data,
        'sensor': "true" if from_sensor else "false"
    }
    url = googleGeocodeUrl + urllib.urlencode(params)
    json_response = urllib.urlopen(url)
    response = simplejson.loads(json_response.read())
    if response['results']:
        location = response['results'][0]['geometry']['location']
        latitude, longitude = location['lat'], location['lng']
        print incident_location_data, latitude, longitude
    else:
        latitude, longitude = None, None
        print incident_location_data, "Could not generate coordinates for this Incident"
    return latitude, longitude

def gross_hourly_most_common(request):
  incident_list = Incident.objects.all()
  abstract_hour_list = []
  for i in incident_list:
    time = i.datetime
    hour = time.hour
    abstract_hour_list.extend([hour])
  x = Counter(abstract_hour_list)
  sorted_x = sorted(x.items(), key=operator.itemgetter(0))
  x_values = [x[1] for x in sorted_x]
  context = {'x_values':x_values,'incident_list': incident_list}

  return render(request, 'dashboard.html', context)
  #pdb.set_trace()

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
