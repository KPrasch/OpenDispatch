
import requests
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import viewsets

from django.shortcuts import render
from rest_framework.renderers import JSONRenderer

from apps.map.models import *
from apps.map.serializers import IncidentGeoSerializer, IncidentListSerializer
from private.dispatch_settings import *
from private.secret_settings import *
from collections import OrderedDict

import logging
logger = logging.getLogger('geocoder')


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


class IncidentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = Incident.objects.order_by('-dispatch_time')
    serializer_class = IncidentGeoSerializer

    @list_route(renderer_classes=[JSONRenderer])
    def geo(self, request, *args, **kwargs):
        queryset = Incident.objects.order_by('-dispatch_time')
        serializer = IncidentGeoSerializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(renderer_classes=[JSONRenderer])
    def recent(self, request, *args, **kwargs):
        queryset = Incident.objects.all().order_by('-dispatch_time')[0]
        serializer = IncidentListSerializer(queryset)
        return Response(serializer.data)


def compile_incident_location_string(incident_dict):
    """
    Gather the required search text from the incident dict.
    """
    loc_string = ''
    for key in STREET_ADDRESS_KEYS:
        if key in incident_dict:
            loc_string += str(incident_dict[key]) + ', '
        else:
            logger.warn("No value for key %s" % key)

    for key in VENUE_KEYS:
        if key in incident_dict:
            loc_string += str(incident_dict[key])
        else:
            logger.warn("No value for key %s" % key)

    incident_location_string = (loc_string.lower().title()).encode('utf-8')
    
    return incident_location_string


def geocode(incident_location_string, from_sensor=False, strict=True, round=1):
    """
    Uses the unauthenticated Google Maps API V3.  using passed incident location string, return a latitude and logitude for an incident. 
    """

    logger.info("Geocoding %s ..." % incident_location_string)

    if incident_location_string == '' or incident_location_string is None:
        logger.error('Empty incident strings cannot be geocoded.')
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
            logger.error("Failed to generate coordinates for an Incident\n Status: %s\n Reason: %s\n Payload: %s" % \
                         (error, reason, payload))

        elif response['status'] == "ZERO_RESULTS":
            if round == 1:
                geocode(incident_location_string, strict=False, round=2)
                logger.info("Zero results for %s \n trying again with strict = False" % incident_location_string)
            elif round == 2:
                # Do something more recursive, again...?
                logger.warn("No Location Found after removing strict filtration. Payload: %s" % incident_location_string)
                latitude, longitude = None, None

        elif response['status'] == 'OK':
            result = response['results'][0]['geometry']
            location = result['location']
            accuracy = result['location_type']
            latitude, longitude = location['lat'], location['lng']

            logger.info(incident_location_string, accuracy, latitude, longitude)

        else:
            latitude, longitude = None, None
            reason = response["status"]
            logger.warn(incident_location_string, "Could not generate coordinates for this Incident - Reason: %s" % reason)
    else:
        logger.error("%s" % re.status_code)
        # Do Something!

    return latitude, longitude
