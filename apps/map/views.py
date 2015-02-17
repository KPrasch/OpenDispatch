

def get_zipcode():
    '''
    Identify the postal zip code for an incident
    '''
    pass

def compile_incident_location_string(incident_dict):
    '''
    Gather the required search text from the incident dict.
    '''
    location_fields = dispatch_settings.LOCATION_FIELDS
    incident_location_list = [incident_dict[x] for x in location_fields]
    incident_location_string = string.lower(" ".join(incident_location_list)) + dispatch_settings.LOCALE_STATE.encode('utf-8')
    
    return incident_location_string

def get_coordinates(incident_dict, from_sensor=False):
    '''
    Uses the unauthenticated Google Maps API V3.  using passed incident string, return a latitude and logitude for an incident. 
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
        print incident_location_data, latitude, longitude
    else:
        latitude, longitude = None, None
        print incident_location_data, "Could not generate coordinates for this Incident"
        
    return latitude, longitude
