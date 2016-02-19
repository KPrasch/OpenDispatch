from __future__ import unicode_literals
from datetime import datetime
import getpass
import email
import time
import json
import imaplib
import unicodedata
import urllib
from urlparse import parse_qs

import re
from dateutil import parser
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.http import HttpResponse
import simplejson

from rest_framework.response import Response
import requests
from requests_oauthlib import OAuth1
from hendrix.contrib.async.messaging import hxdispatcher
from hendrix.experience import crosstown_traffic

from rest_framework.renderers import JSONRenderer

from rest_framework.decorators import api_view, renderer_classes
from rest_framework import status

from django.db.models import Q

from apps.map.models import Incident, IncidentMeta, FixedLocation, WeatherSnapshot
from apps.map.views import compile_incident_location_string, geocode
from apps.map.serializers import IncidentGeoSerializer
from private.secret_settings import *
from private.dispatch_settings import *


def setup_oauth():
    """Authorize your app via identifier."""
    # Request token
    oauth = OAuth1(TWITTER_CONSUMER_KEY, client_secret=TWITTER_CONSUMER_SECRET)
    r = requests.post(url=TWITTER_REQUEST_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)

    resource_owner_key = credentials.get('oauth_token')[0]
    resource_owner_secret = credentials.get('oauth_token_secret')[0]

    # Authorize
    authorize_url = TWITTER_AUTHORIZE_URL + resource_owner_key
    print 'Please go here and authorize: ' + authorize_url

    verifier = raw_input('Please input the verifier: ')
    oauth = OAuth1(TWITTER_CONSUMER_KEY,
                   client_secret=TWITTER_CONSUMER_SECRET,
                   resource_owner_key=resource_owner_key,
                   resource_owner_secret=resource_owner_secret,
                   verifier=verifier)

    # Finally, Obtain the Access Token
    r = requests.post(url=TWITTER_ACCESS_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)
    token = credentials.get('oauth_token')[0]
    secret = credentials.get('oauth_token_secret')[0]

    return token, secret


def get_oauth():
    oauth = OAuth1(TWITTER_CONSUMER_KEY,
                client_secret=TWITTER_CONSUMER_SECRET,
                resource_owner_key=TWITTER_OAUTH_TOKEN,
                resource_owner_secret=TWITTER_OAUTH_TOKEN_SECRET)
    return oauth


@csrf_exempt
def stream_twitter():

    @crosstown_traffic()
    def stream():
        if not TWITTER_OAUTH_TOKEN:
            token, secret = setup_oauth()
            print "OAUTH_TOKEN: " + token
            print "OAUTH_TOKEN_SECRET: " + secret

        else:
            oauth = get_oauth()
            r = requests.get(url="https://stream.twitter.com/1.1/statuses/filter.json?follow=951808694", auth=oauth, stream=True)

            for line in r.iter_lines():

                # filter out keep-alive new lines
                if line:
                    #try:
                    incident_dict = json.loads(line)
                    payload = incident_dict["text"]
                    twitter_time = incident_dict["created_at"]
                    # Get twitter's tweet-received time.
                    received_datetime = parser.parse(twitter_time)
                    # Now, do it.
                    process_import(payload, received_datetime)

                    #except ValueError:
                    #    print(line)
                        #hxdispatcher.send("twitter-dispatches", line)
    print "Crosstown Traffic Thread Listening for Tweets ...\n"
    return HttpResponse(status=200)


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def search_incidents(request):
    """
    Autocomplete
    """
    #import pdb; pdb.set_trace()
    q = request.GET.get('term')

    if q == '':
        matches = Incident.objects.all().order_by("-dispatch_time")
    else:
        matches = Incident.objects.all().filter(Q(meta__dispatch__icontains=q) |
                                                Q(meta__venue__icontains=q) |
                                                Q(location__street_address__icontains=q)) \
                                                .order_by("-dispatch_time")

    serializer = IncidentGeoSerializer(matches, many=True)

    if bool(matches) is True:
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


def parse_incident(payload, twitter=False):
    """
    Using configurable incident data fields, parse the data into incident models with all of the information required.
    """

    keys = set(ESCAPE_KEYS)
    key_re = re.compile('(' + '|'.join(re.escape(key) for key in keys) + '):', re.IGNORECASE)
    key_locations = key_re.split(payload)[1:]
    incident_dict = {k: v.strip() for k, v in zip(key_locations[::2], key_locations[1::2])}

    if twitter is False:
        regex = re.compile('[^a-zA-Z]')
        incident_dict['Venue'] = str.rstrip(regex.sub(" ", incident_dict['Venue']))

    elif twitter is True:
        regex = re.compile("([a-zA-Z_ ]*)([^a-zA-Z]*)$")
        s = regex.search(incident_dict["Venue"])

        if s.groups()[1] is not '':
            # Adding a key to the dictionary here.
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
    return response


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
        print "Duplicate Incident. (Probably the the Twitter Streaming API back filling from a recent reconnection.)"
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

    incidentmeta.save()
    incident.save()
    print "Created %d" % incident.id
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

