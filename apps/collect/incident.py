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
from apps.map.geo import compile_incident_location_string, geocode
from apps.map.serializers import IncidentGeoSerializer
from private.dispatch_settings import *
from apps.people.views import notify_users_in_radius

default_logger = logging.getLogger('django')
auth_logger = logging.getLogger('auth')
telephony_logger = logging.getLogger('telephony')


def get_weather_snapshot(lng, lat):
    """
    Uses the unauthenticated Google Maps API V3.  using passed incident location string, return a latitude and logitude for an incident.
    """
    openWeatherMapsUrl = 'http://api.openweathermap.org/data/2.5/weather?'
    params = {
        'lat': lat,
        'lon': lnn,
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

    return weathersnapshot


def map_intelligence_filter(incident_dict):
    # NLTK
    # Proximity to User Set Locations
    # Thruway Detection
    # Mutual Aid Detection
    # Out of Locale Detection
    # 2nd Alarm detection
    # Target Hazard Detection
    # MediVac / LZ Detection
    # Proximity to Preplaned Structures
    pass


def process_import(bulletin):
    """
    Manages the overall process of importing incidents.
    """

    normalize = normalize_incident_data(bulletin.payload)
    incident_dict = parse_incident(normalize, twitter=True)
    loc_str = compile_incident_location_string(incident_dict)
    geo = geocode(loc_str)
    lat = geo[0]; lng = geo[1]
    #if incident_dict["Venue"] is "":

    # Branch after this line for multiple incidents in one location.
    fixed_loc = FixedLocation.objects.get_or_create(lat=lat, lng=lng, street_address=loc_str)

    try:
        incident = Incident.objects.create(payload=bulletin.payload, location=fixed_loc[0], received_time=bulletin.received_dt,
                                           dispatch_time=incident_dict["dispatch_time"])

    # Explore if incidents are validated for duplicates well enough.  Twitter Stream API does in fact send dupes.
    except IntegrityError:
        default_logger.warn("Duplicate Incident. (Probably the the Twitter Streaming API back filling from a recent reconnection.)")
        return HttpResponse(status=200)

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

    '''
    # @crosstown_traffic()
    def notify():
        notify_users_in_radius(incident, firehose=True)
        telephony_logger.info("Finished Notifying Users.")
        return
    '''

    incident.save()
    default_logger.info("Created %d" % incident.id)

    # Broadcast that the data is stale to everyone
    hxdispatcher.send("twitter-dispatches", {"status": "stale"})
    return incident


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

