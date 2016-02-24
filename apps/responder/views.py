from django.shortcuts import render
from django.db.models import Q
from apps.map.models import Incident
from private.responder_settings import *
from datetime import datetime


def responder_board(request, venue=None):
    """
    Return the Template
    """
    if venue is None:
        recent_incidents = Incident.objects.all().order_by("-dispatch_time")
    else:
        max_dt = datetime.now()
        min_dt = max_dt - BOARD_INCIDENT_AUTOCLEAR_TIME_IN_HOURS

        recent_incidents = Incident.objects.filter(Q(meta__venue__icontains=venue) |
                                                 Q(dispatch_time__range=[min_dt, max_dt])
                                                 ).order_by("-dispatch_time")
    return render(request, 'app/responder/board.html', {"past_incidents": recent_incidents})


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