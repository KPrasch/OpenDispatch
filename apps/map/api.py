from collections import OrderedDict
from datetime import datetime
import logging

from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from django.db.models import Q
from apps.map.models import *
from apps.map.serializers import IncidentGeoSerializer, IncidentListSerializer

logger = logging.getLogger('geocoder')


class InsightViewSet(viewsets.GenericViewSet):
    queryset = Incident.objects.order_by('-dispatch_time')
    serializer_class = IncidentListSerializer

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
    serializer_class = IncidentListSerializer

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

        serializer = IncidentListSerializer(self.queryset, many=True)
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

        serializer = IncidentListSerializer(queryset, many=many)
        return Response(serializer.data)

    @list_route(renderer_classes=[JSONRenderer], url_path='venue/(?P<venue>.*)')
    def venue(self, request, venue):
        queryset = self.queryset.filter(meta__venue__icontains=venue)
        serializer = IncidentListSerializer(queryset, many=True)
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
