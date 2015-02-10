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


googleGeocodeUrl = 'http://maps.googleapis.com/maps/api/geocode/json?'

def get_coordinates(incident_location_data, from_sensor=False):
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
