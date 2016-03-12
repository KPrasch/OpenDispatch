from __future__ import unicode_literals
from datetime import datetime
import getpass
import email
import time
import imaplib
import unicodedata
import urllib
import logging

import re
from dateutil import parser
from django.db import IntegrityError
from django.http import HttpResponse
import simplejson
from hendrix.contrib.async.messaging import hxdispatcher

from apps.map.models import Incident, IncidentMeta, FixedLocation, WeatherSnapshot
from apps.map.views import compile_incident_location_string, geocode
from apps.map.serializers import IncidentGeoSerializer
from private.dispatch_settings import *
from apps.people.views import notify_users_in_radius

default_logger = logging.getLogger('django')
auth_logger = logging.getLogger('auth')
telephony_logger = logging.getLogger('telephony')


def parse_incident(payload, twitter=False):
    """
    Using configurable incident data fields, parse the data into incident models with all of the information required.
    """

    keys = set(ESCAPE_KEYS)
    key_re = re.compile('(' + '|'.join(re.escape(key) for key in keys) + '):', re.IGNORECASE)
    key_locations = key_re.split(payload)[1:]
    incident_dict = {k: v.strip() for k, v in zip(key_locations[::2], key_locations[1::2])}

    try:
        if twitter is False:
            regex = re.compile('[^a-zA-Z]')
            incident_dict['Venue'] = str.rstrip(regex.sub(" ", incident_dict['Venue']))

        elif twitter is True:
            regex = re.compile("([a-zA-Z_ ]*)([^a-zA-Z]*)$")
            s = regex.search(incident_dict["Venue"])

            if s.groups()[1] is not '':
                # Adding a key to the dictionary here (dispatch time).
                incident_dict['dispatch_time'] = parser.parse(s.groups()[1])
                incident_dict['Venue'] = str.rstrip(s.groups()[0])

                if "king" in incident_dict['Venue'].lower():
                    incident_dict["Venue"] = "Kingston"
                elif "out of" in incident_dict["Venue"].lower():
                    incident_dict["Venue"] = ""
                    # Handle out of City Dispatches here.

            else:
                regex = re.compile('[^a-zA-Z]')
                incident_dict['Venue'] = str.rstrip(regex.sub(" ", incident_dict['Venue']))
    except KeyError as e:
        default_logger.warn("Can not manipulate dictionary {0} - {1}".format(incident_dict, e))

    return incident_dict


def normalize_incident_data(payload):
    """
    Converts unicode data to a python string.
    """
    payload = payload.replace('\n', '').replace('\r', '')
    try:
        payload =  unicodedata.normalize('NFKD', payload).encode('ascii', 'ignore') 
    except TypeError:
        # If this isn't unicode, and already a string
        pass
    
    return payload


def get_weather_snapshot(lon, lat):
    """
    Uses the unauthenticated Google Maps API V3.  using passed incident location string, return a latitude and logitude for an incident.
    """
    openWeatherMapsUrl = 'http://api.openweathermap.org/data/2.5/weather?'
    params = {
        'lat': lat,
        'lon': lon,
        'APPID': '9b147b4afb5679767ae2c445e841da60'
    }
    url = openWeatherMapsUrl + urllib.urlencode(params)
    json_response = urllib.urlopen(url)
    r = simplejson.loads(json_response.read())

    weathersnapshot = WeatherSnapshot.create(description=r["weather"][0]["description"],
                                             wind_speed=r["wind"]["speed"],
                                             wind_heading=r["wind"]["deg"],
                                             temperature=r["main"]["temp"],
                                             clouds=r["clouds"]["all"])

    import pdb; pdb.set_trace()
    pass


def map_intelligence_filter(incident_dict):
    # Proximity to User Set Locations
    # Thruway Detection
    # Mutual Aid Detection
    # Out of Locale Detection
    # 2nd Alarm detection
    # Target Hazard Detection
    # MediVac / LZ Detection
    # Proximity to Preplaned Structures
    pass


def process_import(incident_str, received_datetime):
    """
    Manages the overall process of importing incidents.
    """

    normalize = normalize_incident_data(incident_str)
    incident_dict = parse_incident(normalize, twitter=True)
    loc_str = compile_incident_location_string(incident_dict)
    geo = geocode(loc_str)
    lat = geo[0]; lng = geo[1]
    #if incident_dict["Venue"] is "":

    # Branch after this line for multiple incidents in one location.
    fixed_loc = FixedLocation.objects.get_or_create(lat=lat, lng=lng, street_address=loc_str)

    try:
        incident = Incident.objects.create(payload=incident_str, location=fixed_loc[0], received_time=received_datetime,
                                           dispatch_time=incident_dict["dispatch_time"])

    # Explore if incidents are validated for duplicates well enough.  Twitter Stream API does in fact send dupes.
    except IntegrityError:
        default_logger.warn("Duplicate Incident. (Probably the the Twitter Streaming API back filling from a recent reconnection.)")
        return HttpResponse(status=200)

    # weathersnapshot = WeatherSnapshot.objects.create()
    incidentmeta = IncidentMeta.objects.create(incident=incident)

    for key, value in incident_dict.items():
        if key in VENUE_KEYS:
            incidentmeta.venue = value
            incidentmeta.location = value
        elif key in INCIDENT_KEYS:
            incidentmeta.dispatch = value
        elif key in INTERSECTION_KEYS:
            incidentmeta.intersection = value
        elif key in UNIT_KEYS:
            incidentmeta.unit = value
        elif key in LOCATION_KEYS:
            pass
            # Ugh...
        else:
            # Got something else....?
            pass

    # @crosstown_traffic()
    def notify():
        notify_users_in_radius(incident, firehose=True)
        telephony_logger.info("Finished Notifying Users.")

    incidentmeta.save()
    incident.save()
    default_logger.info("Created %d" % incident.id)
    # hxdispatcher.send("twitter-dispatches", "Created %d" % incident.id)

    serializer = IncidentGeoSerializer(incident)
    hxdispatcher.send("twitter-dispatches", serializer.data)
    return HttpResponse(status=201)


def get_email_incidents(request, username):
    """
    This view connects to an individuals gmail inbox, selects emails sent from 911 Dispatch,
    by sender address, and saves the emails to the database.
    """
    usernm = raw_input("Username:")
    passwd = getpass.getpass(prompt='Password: ', stream=None)
    conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    conn.login(usernm,passwd)
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

