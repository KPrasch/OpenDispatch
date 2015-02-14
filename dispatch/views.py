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


def import_incidents(request, source):
    '''
    Master incident import view.  Used for the initial population of the dispatch database.
    Incidents must be unique in the databse, or ProgrammingError is raised.
    '''
    if source == 'twitter':
      get_twitter_incidents(dispatch_settings.TWITTER_USERNAME)
      return source
    elif source == 'email':
      get_email_incidents(dispatch_settings.EMAIL_USERNAME)
      return source
    else:
      raise ValueError("Invalid dispatch source.  Please specify twitter, email or cad.")  

def process_import(incident_str, recieved_datetime):
    '''
    '''
    normalize = normalize_incidnt_data(incident_str)
    parse = parse_incident(normalize.payload)
    incident_dict = parse.incident_dict
    loc_str = incident_location_string(incident_dict)
    geocode = get_coordinates(loc_str.incident_location_string)
    lat = geocode[0]; lng = geocode[1]
    
    try: 
        incident = Incident.objects.create(recieved_datetime = recieved_datetime, lat = lat, lng = lng)
        incident.save()
    except ProgrammingError:
        pass

    for key,value in incident_dict:
        incident_data = IncidentData.objects.create(**locals())
        incident_data.save()
            
        print "Created Incident %d" % incident.id
        return HttpResponse(status=201)
    
    return HttpResponse(status=200)

def get_current_weather(zip):
    '''
    '''
    #Slightly more lacal.
    weather_com_result = pywapi.get_weather_from_weather_com(zip)
    yahoo_result = pywapi.get_weather_from_yahoo(zip)
    #Gather the bulk of the weather data from NOAA.
    noaa_result = pywapi.get_weather_from_noaa(dispatch_settings.NOAA_STATION_CALL_SIGN)
    

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
    
    return incident_dict

def get_zipcode():
    pass

def compile_incident_location_string(incident_dict):
    #Gather the required search text from the incident dict.
    location_fields = dispatch_settings.LOCATION_FIELDS
    incident_location_list = [incident_dict[x] for x in location_fields]
    incident_location_string = string.lower(" ".join(incident_location_list)) + dispatch_settings.LOCALE_STATE.encode('utf-8')
    
    return incident_location_string

def get_coordinates(incident_dict, from_sensor=False):
    '''
    Uses the unauthenticated Google Maps API V3.  using passed incident dictionary,
    gather relevant location text and return a latitude and logitude for an incident. 
    '''

      
    #Now lookups the incident's coordinates.
    googleGeocodeUrl = 'http://maps.googleapis.com/maps/api/geocode/json?'
    params = {
        'address': incident_location_string,
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
