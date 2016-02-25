from django.shortcuts import render
from django.db.models import Q
from apps.map.models import Incident
from private.responder_settings import *
from apps.map.serializers import IncidentGeoSerializer, IncidentMetaSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, renderer_classes
import datetime


def responder_board(request, venue=None):
    """
    Return the Template
    """
    return render(request, 'app/responder/board.html')


@api_view(['GET'])
def get_recent_incidents(request, venue=None):
    if venue is None:
        recent_incidents = Incident.objects.all().order_by("-dispatch_time")
    else:
        max_dt = datetime.datetime.now()
        min_dt = max_dt - datetime.timedelta(minutes=BOARD_INCIDENT_AUTOCLEAR_TIME_IN_MINUTES)

        recent_incidents = Incident.objects.filter(Q(meta__venue__icontains=venue) &
                                                 Q(dispatch_time__range=[min_dt, max_dt])
                                                 ).order_by("-dispatch_time")

    geo_serializer = IncidentGeoSerializer(recent_incidents, many=True)

    return Response(geo_serializer.data, status=status.HTTP_200_OK)

"""
# Try adding your own number to this list!
callers = {
    "+18456331959": "Kieran",
}

@api_view(['GET, POST'])
def hello_monkey(request):
    # Get the caller's phone number from the incoming Twilio request
    from_number = request.values.get('From', None)
    resp = twilio.twiml.Response()
 
    # if the caller is someone we know:
    if from_number in callers:
        # Greet the caller by name
        resp.say("Hello " + callers[from_number])
    else:
        resp.say("Hello Monkey")
 
    return Response(status=status.HTTP_200_OK)
"""