import datetime

from django.shortcuts import HttpResponse
from django.db.models import Q
import twilio.twiml
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from hendrix.experience import crosstown_traffic
from hendrix.contrib.async.messaging import hxdispatcher
from django.core.exceptions import ObjectDoesNotExist

from apps.map.models import Incident
from apps.map.serializers import IncidentGeoSerializer
from apps.people.models import Account
from private.responder_settings import *
from apps.people.serializers import AccountModelSerializer
import logging

default_logger = logging.getLogger('django')


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

@csrf_exempt
def initiate_personnel_response(request):

    if request.method == 'POST':

        most_recent = Incident.objects.all()[0]
        # Get the caller's phone number from the incoming Twilio request
        # from_number = request.POST.get("From")
        from_number = request.POST.get('From')
        default_logger.info("response call from {}".format(from_number))

        resp = twilio.twiml.Response()

        try:
            user = Account.objects.get(phone_number=from_number)
            if user.is_responder is True and user.responder_active is True:
                responder = user
                message = "Hello {0}, press any key to respond with E.T.A.\
                    The most recent dispatch, was dispatched at {1}. to. {2}. for. {3}." \
                    .format(responder.user.first_name,
                            most_recent.dispatch_time,
                            most_recent.location.street_address,
                            most_recent.meta.dispatch)

                with resp.gather(numDigits=1, action="/handle_key/%s" % responder.id, method="POST") as g:
                    g.say(message)

            else:
                message = "You are not authorized to respond."

        except ObjectDoesNotExist:
            message = "You have reached a Responder Zero phone number. You do not have an account. Goodbye."

        resp.say(message)
        return HttpResponse(str(resp))


@csrf_exempt
def confirm_personnel_response(request, responder_id):

    if request.method == 'POST':

        # Get the digit pressed by the user
        digit_pressed = request.POST.get('Digits', None)
        responder = Account.objects.get(id=responder_id)

        @crosstown_traffic()
        def respond():
            serializer = AccountModelSerializer(responder)
            hxdispatcher.send("twilio-stream", serializer.data)


        resp = twilio.twiml.Response()
        resp.say("Response Confirmed. Your E.T.A. is %s minutes" % str(digit_pressed))

        return HttpResponse(str(resp))

    else:
        pass