import twilio.twiml
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework import status
 
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
