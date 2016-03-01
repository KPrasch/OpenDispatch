import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import redirect
from django.shortcuts import render
from twilio.rest import TwilioRestClient
from django.contrib.gis.measure import D
import chalk

from apps.map.forms import FixedLocationForm, StructureForm
from apps.people.forms import AccountForm, UserForm, UserLocationForm
from private.secret_settings import TWILIO_SID, TWILIO_SECRET, TWILIO_NUMBER, SMS_DISABLE
from apps.map.models import UserLocation

telephony_logger = logging.getLogger('telephony')


def app_login(request):

    if request.method == 'POST':
        if 'username' not in request.POST or 'password' not in request.POST:
            return Response({"error": "Missing username or password."}, status=status.HTTP_406_NOT_ACCEPTABLE)

        usernm = request.POST['username']
        passwd = request.POST['password']
        user = authenticate(username=usernm, password=passwd)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/map/')
            else:
                # Return a 'disabled account' error message
                error = "Your account has been disabled."
        else:
            # Return an 'invalid login' error message.
            error = "Invalid Login User and Password Combination."

        return Response({"error": error}, status=status.HTTP_403_FORBIDDEN)
    else:
        user_form = UserForm()
        account_form = AccountForm()
        user_location_form = UserLocationForm()
        fixed_location_form = FixedLocationForm()

        structure_form = StructureForm()
        return render(request, 'global/public_auth.html', {"account_form": account_form,
                                                           "user_form": user_form,
                                                           "user_location_form": user_location_form,
                                                           "fixed_location_form": fixed_location_form,
                                                           "structure_form": structure_form})


def logout_view(request):
    logout(request)
    return redirect('/dispatches/')


def registration(request):
    pass


def notify_users_in_radius(incident, firehose=True):
    if SMS_DISABLE:
        chalk.magenta("SMS_DISABLE is currently true, no users are notified.")
        return incident.id

    if incident.id == None:
        print "No incident object received when attemping to notify user."
        return

    client = TwilioRestClient(TWILIO_SID, TWILIO_SECRET)
    radius = 100 if firehose is True else 20

    nearby_uls = UserLocation.objects.filter(poi__point__distance_lte=(incident.location.point, D(mi=radius)))

    for user_location in nearby_uls:
        account = user_location.account
        phone_number = str(account.phone_number)
        sms_body = incident.sms_str(user_location)
        message = client.messages.create(to=phone_number, from_=TWILIO_NUMBER, body=sms_body)
        telephony_logger.info("Sending SMS to %s: %s" % (account.user.first_name + account.user.last_name, str(account.phone_number)))

    return nearby_uls.count()
