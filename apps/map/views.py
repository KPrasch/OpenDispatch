# Import django modules
import string
import urllib

import simplejson
import requests
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response

from django.shortcuts import render
from rest_framework.renderers import JSONRenderer

from apps.map.models import *
from apps.map.serializers import IncidentGeoSerializer
from private.dispatch_settings import *
from private.secret_settings import *
from collections import OrderedDict


def map_view(request, venue=None):
    """
    Return the Template
    """
    if venue is None:
        past_incidents = Incident.objects.all().order_by("-dispatch_time")
    else:
        past_incidents = Incident.objects.filter(meta__venue__icontains=venue).order_by("-dispatch_time")

    incident_types = {pi.meta.dispatch for pi in past_incidents if pi.meta.dispatch}
    incident_counts = (past_incidents.filter(meta__dispatch=i).count() for i in incident_types)
    mapped_values = dict(zip(incident_types, incident_counts))
    ordered_values = OrderedDict(sorted(mapped_values.items(), key=lambda t: t[1]))

    venues = {inc.meta.venue for inc in past_incidents}
    venue_counts = (past_incidents.filter(meta__venue=v).count() for v in venues)
    pie_chart = dict(zip(venues, venue_counts))
    sorted_pie = OrderedDict(sorted(pie_chart.items(), key=lambda t: t[1]))

    return render(request, 'app/map/map.html', {"incidents": past_incidents, "incident_types":  incident_types,
                                                "incident_chart": ordered_values,
                                                "pie_chart": sorted_pie,
                                                "venue_filter": venue,
                                                "locale_state": LOCALE_STATE})


def bubble_view(request):
    """
    Return the Template
    """
    return render(request, 'app/graph.html')


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def most_recent_dispatch(request):
    """
    Most Recent Dispatch in GeoJSON
    """
    recent = Incident.objects.all().order_by("-dispatch_time")[0]
    serializer = IncidentGeoSerializer(recent)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def get_geoincidents(request, venue=None):
    """
    FeatureCollection list of all Incidents in GeoJSON

    {"type":"FeatureCollection","features":[]}

    """
    if venue is None:
        geoincidents = Incident.objects.all().order_by('-dispatch_time')
    else:
        geoincidents = Incident.objects.all().filter(meta__venue__icontains=venue).order_by('-dispatch_time')

    serializer = IncidentGeoSerializer(geoincidents, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


def compile_incident_location_string(incident_dict):
    """
    Gather the required search text from the incident dict.
    """
    loc_string = ''
    for key in STREET_ADDRESS_KEYS:
        if key in incident_dict:
            loc_string += str(incident_dict[key]) + ', '
        else:
            print "No value for key %s" % key

    for key in VENUE_KEYS:
        if key in incident_dict:
            loc_string += str(incident_dict[key])
        else:
            print "No value for key %s" % key

    incident_location_string = (loc_string.lower().title()).encode('utf-8')
    
    return incident_location_string


def geocode(incident_location_string, from_sensor=False, strict=True, round=1):
    """
    Uses the unauthenticated Google Maps API V3.  using passed incident location string, return a latitude and logitude for an incident. 
    """

    print "Geocoding %s ..." % incident_location_string

    if incident_location_string == '' or incident_location_string is None:
        raise ValueError('Empty incident strings cannot be geocoded.')

    url = 'https://maps.googleapis.com/maps/api/geocode/json?'

    geocoder_restrictions = "country:" + LOCALE_COUNTRY + "|administrative_area:" + LOCALE_STATE

    if strict is True:
        geocoder_restrictions += "|administrative_area:" + LOCALE_ADMIN_REGION

    params = {
        'key': GOOGLE_SERVER_KEY,
        'address': incident_location_string,
        'sensor': "true" if from_sensor else "false",
        'components': geocoder_restrictions
        }

    re = requests.get(url=url, params=params)

    if re.status_code == 200:
        response = re.json()

        if "error_message" in response:
            latitude, longitude = None, None
            error = response["status"]
            reason = response["error_message"]
            payload = incident_location_string
            print "Could not generate coordinates for an Incident\n Status: %s\n Reason: %s\n Payload: %s" % (error, reason, payload)

        elif response['status'] == "ZERO_RESULTS":
            if round == 1:
                geocode(incident_location_string, strict=False, round=2)
                print "Zero results for %s \n trying again with strict = False" % incident_location_string
            elif round == 2:
                # Do something more recursive, again...?
                print "No Location Found. Payload: %s" % incident_location_string
                latitude, longitude = None, None

        elif response['status'] == 'OK':
            result = response['results'][0]['geometry']
            location = result['location']
            accuracy = result['location_type']
            latitude, longitude = location['lat'], location['lng']

            print incident_location_string, accuracy, latitude, longitude

        else:
            latitude, longitude = None, None
            reason = response["status"]
            print incident_location_string, "Could not generate coordinates for this Incident - Reason: %s" % reason
    else:
        print "%s" % re.status_code
        import pdb; pdb.set_trace()
        # Do Something!

    return latitude, longitude


