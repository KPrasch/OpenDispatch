# Import django modules
import string
import urllib

from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from map.models import *
from private.dispatch_settings import LOCATION_FIELDS, LOCALE_STATE
import simplejson


def mapView(request):
    'Display map'
    incidents = Incident.objects.order_by('received_time')
    return render_to_response('app/map/map.html', {
        'incidents': incidents,
        'content': render_to_string('app/map/map.html', {'incidents': incidents}),
    })

def get_zipcode():
    '''
    Identify the postal zip code for an incident
    '''
    pass

def compile_incident_location_string(incident_dict):
    '''
    Gather the required search text from the incident dict.
    '''
    location_fields = LOCATION_FIELDS
    incident_location_list = [incident_dict[x] for x in location_fields]
    incident_location_string = string.lower(" ".join(incident_location_list)) + " " + LOCALE_STATE.encode('utf-8')
    
    return incident_location_string

def geocode(incident_location_string, from_sensor=False):
    '''
    Uses the unauthenticated Google Maps API V3.  using passed incident location string, return a latitude and logitude for an incident. 
    '''
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
        print incident_location_string, latitude, longitude
    else:
        latitude, longitude = None, None
        print incident_location_string, "Could not generate coordinates for this Incident"
        
    return latitude, longitude
