def parse_geostring(incident: dict) -> str:
    """
    Gather the required search text from the incident dict.
    """
    loc_string = str()

    for key in STREET_ADDRESS_KEYS:
        if key in incident:
            loc_string += str(incident[key]) + ', '
        else:
            print(f"No value for key {key}")

    for key in VENUE_KEYS:
        if key in incident:
            loc_string += str(incident[key])
        else:
            print(f"No value for key {key}")

    incident_location_string = loc_string.lower().title()
    return incident_location_string


# def get_weather_snapshot(lon, lat):
#     """
#     Uses the unauthenticated Google Maps API V3.  using passed incident location string, return a latitude and logitude for an incident.
#     """
#     openWeatherMapsUrl = 'http://api.openweathermap.org/data/2.5/weather?'
#     params = {
#         'lat': lat,
#         'lon': lon,
#         'APPID': '9b147b4afb5679767ae2c445e841da60'
#     }
#     url = openWeatherMapsUrl + urllib.urlencode(params)
#     json_response = urllib.urlopen(url)
#     r = simplejson.loads(json_response.read())
#
#     # call backend here.
#
#     # return response


def map_intelligence_filter(incident: dict):
    """
    - Proximity to User Set Locations
    - Thruway Detection
    - Mutual Aid Detection
    - Out of Locale Detection
    - 2nd Alarm detection
    - Target Hazard Detection
    - MediVac / LZ Detection
    - Proximity to Preplaned Structures
    """


def process_incident(incident: dict):
    """
    Manages the overall process of importing incidents.
    """
    geostring = parse_geostring(incident)
    geo = googlev3_geocoder(geostring)
    lat, lng = geo[0], geo[1]

    # incident = None
    # incident.json()
    # return incident
