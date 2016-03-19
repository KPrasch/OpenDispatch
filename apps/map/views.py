from collections import OrderedDict
from datetime import datetime
import logging

import requests
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from django.shortcuts import render
from rest_framework.renderers import JSONRenderer
from django.db.models import Q

from apps.map.models import *
from apps.map.serializers import IncidentGeoSerializer, IncidentSerializer
from private.dispatch_settings import *
from private.secret_settings import *
from itertools import islice

logger = logging.getLogger('geocoder')


class InsightViewSet(viewsets.GenericViewSet):
    queryset = Incident.objects.order_by('-dispatch_time')
    serializer_class = IncidentSerializer

    @list_route(renderer_classes=[JSONRenderer])
    def top_dispatches(self, request, *args, **kwargs):

        incident_types = {pi.meta.dispatch for pi in self.queryset if pi.meta.dispatch}
        incident_counts = (self.queryset.filter(meta__dispatch=i).count() for i in incident_types)
        mapped_values = dict(zip(incident_types, incident_counts))
        chart = OrderedDict(sorted(mapped_values.items(), key=lambda mv: mv[1]))

        return Response(chart)

    @list_route(renderer_classes=[JSONRenderer])
    def top_venues(self, request, *args, **kwargs):

        venues = {inc.meta.venue for inc in self.queryset if inc.meta.venue != ''}
        venue_counts = (self.queryset.filter(meta__venue=v).count() for v in venues)
        pie_chart = dict(zip(venues, venue_counts))
        chart = OrderedDict(sorted(pie_chart.items(), key=lambda t: t[1]))

        return Response(chart)

    @list_route(renderer_classes=[JSONRenderer])
    def top_intersections(self, request, *args, **kwargs):
        intersections = {inc.meta.intersection for inc in self.queryset if inc.meta.intersection != ''}
        intersection_counts = (self.queryset.filter(meta__intersection=v).count() for v in intersections)
        pie_chart = dict(zip(intersections, intersection_counts))
        chart = OrderedDict(sorted(pie_chart.items(), key=lambda t: t[1]))

        return Response(chart)


class IncidentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = Incident.objects.order_by('-dispatch_time')
    serializer_class = IncidentSerializer

    def list(self, request):
        active = request.GET.get('active')
        venue = request.GET.get('venue')
        start_datetime = request.GET.get('min')
        end_datetime = request.GET.get('max')

        if start_datetime and end_datetime:
            min_dt = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M:%S.%fZ')
            max_dt = datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M:%S.%fZ')

            self.queryset.filter(dispatch_time__range=[min_dt, max_dt])

        if active == 'true':
            self.queryset.filter(active=True)

        if venue:
            self.queryset.filter(meta__venue__icontains=venue)

        serializer = IncidentSerializer(self.queryset, many=True)
        return Response(serializer.data)

    @list_route(renderer_classes=[JSONRenderer])
    def geo(self, request):
        serializer = IncidentGeoSerializer(self.queryset, many=True)
        return Response(serializer.data)

    @list_route(renderer_classes=[JSONRenderer])
    def recent(self, request):
        q = request.GET.get('count')

        if q is not None:
            queryset = self.queryset[0:int(q)]
            many = True
        else:
            queryset = self.queryset[0]
            many = False

        serializer = IncidentSerializer(queryset, many=many)
        return Response(serializer.data)

    @list_route(renderer_classes=[JSONRenderer], url_path='venue/(?P<venue>.*)')
    def venue(self, request, venue):
        queryset = self.queryset.filter(meta__venue__icontains=venue)
        serializer = IncidentSerializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(renderer_classes=[JSONRenderer])
    def contains(self, request):
        q = request.GET.get('term')

        if q != '':
            queryset = self.queryset.filter(Q(meta__dispatch__icontains=q) |
                                            Q(meta__venue__icontains=q) |
                                            Q(location__street_address__icontains=q))

        serializer = IncidentGeoSerializer(queryset, many=True)

        if bool(queryset) is True:
            return Response(serializer.data)
        else:
            return Response(serializer.data)


def map_view(request):
    """
    Return the Template
    """

    return render(request, 'map.html')


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
