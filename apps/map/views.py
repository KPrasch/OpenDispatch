# Import django modules
import re
import string
import urllib

from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from map.models import Incident
from private.dispatch_settings import LOCATION_FIELDS, LOCALE_STATE, LOCALE_COUNTY, KEYS
import simplejson


def mapView(request):
    'Display map'
    incidents = Incident.objects.all().order_by('received_time')
    incident_count = range(len(incidents)); del incident_count[0]
    address_points = []
    for i in incidents:
        address_points.append([i.location.location.x, i.location.location.y], )
    return render_to_response('app/map/map.html', {
        'incidents': incidents,
        'incident_count': incident_count,
        'address_points': address_points,
        'content': render_to_string('app/map/map.html', {'incidents': incidents}),
    })

def get_zipcode():
    '''
    Identify the postal zip code for an incident
    '''
    pass

def compile_incident_location(incident_dict):
    '''
    Gather the required search text from the incident dict.
    '''
    location_fields = LOCATION_FIELDS
    dispatch_fields = KEYS
    loc_string = ''
    loc_more = ''
    for key in dispatch_fields:
        if incident_dict.has_key(key):
            if any(char.isdigit() for char in str(incident_dict[key])):
                m = re.findall("(\d+.*?\D*?\s\D*)", str(incident_dict[key]))
                if m != None:
                    for i in range(0,len(m)):
                        loc_more+=str(m[i] + " ")
                elif m == None:
                    pass
                else:
                    pass
            else:
                pass
        else:
            print "%s not found in this dictionary" % key
            pass
  
    for key in location_fields:
        if incident_dict.has_key(key):
            loc_string+=str(incident_dict[key]) + ' '
        else:
            print "%s not found in this dictionary" % key
            pass
    
    incident_loc_str = (string.lower(loc_string) + " " + LOCALE_STATE + " " + LOCALE_COUNTY).encode('utf-8')
    verbose_loc_str = (string.lower(loc_more) + " " + LOCALE_STATE + " " + LOCALE_COUNTY).encode('utf-8')
    
    return incident_loc_str, verbose_loc_str

def geocode(incident_loc_str, verbose_loc_str, from_sensor=False):
    '''
    Uses the unauthenticated Google Maps API V3.  using passed incident location string, return a latitude and logitude for an incident. 
    '''
    if incident_loc_str == '' or None:
        raise ValueError ("No address string was provided.")
    
    googleGeocodeUrl = 'http://maps.googleapis.com/maps/api/geocode/json?'
    params = {
        'address': incident_loc_str,
        'sensor': "true" if from_sensor else "false"
    }
    
    url = googleGeocodeUrl + urllib.urlencode(params)
    json_response = urllib.urlopen(url)
    response = simplejson.loads(json_response.read())
    
    if response['status'] == 'OVER_QUERY_LIMIT':
        raise Exception("Over Google Geocode API V3 Limit of 2,500 requests per 24 hours, or over 5 requests per second.")
    
    elif response['results']:
        location = response['results'][0]['geometry']['location']
        latitude = location['lat']; longitude = location['lng']
        print incident_loc_str, verbose_loc_str, latitude, longitude
        return latitude, longitude
    else:
        #import pdb; pdb.set_trace()
        print "No Geolocation fix for %s." % incident_loc_str, verbose_loc_str
        print "Searching for nearby locations..." 
        # Invalid geocode result, trying to get a nearby fix by removing numbers from the address. 
        if  incident_loc_str != verbose_loc_str:
            geo = geocode(verbose_loc_str, verbose_loc_str)
        else:
            street_only = ''.join(i for i in incident_loc_str if not i.isdigit())
            geo = geocode(street_only, verbose_loc_str)
            
        latitude = geo[0]; longitude = geo[1]
        return latitude, longitude
        
def mapbox_geocode(incidnet_loction_string):
    '''
    '''
    mapboxGeocodeUrl = 'http://api.tiles.mapbox.com/v4/geocode/' #{index}/{query}.json?access_token=<your access token>
    #index = 
    #query = 
    
    return latitude, longitude 
