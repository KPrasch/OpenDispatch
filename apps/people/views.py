import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import redirect
from django.shortcuts import render
from twilio.rest import TwilioRestClient
from django.contrib.gis.measure import D
from django.http import JsonResponse
import chalk
from rest_framework import viewsets

from apps.map.forms import FixedLocationForm, StructureForm
from apps.people.forms import AccountForm, UserLocationForm
from private.secret_settings import TWILIO_SID, TWILIO_SECRET, TWILIO_NUMBER, SMS_DISABLE
from apps.map.models import UserLocation
from django.shortcuts import get_object_or_404
from apps.people.models import Account
from apps.people.serializers import AccountModelSerializer
from rest_framework.decorators import detail_route, list_route
from rest_framework import permissions
from rest_framework.permissions import AllowAny
from django.shortcuts import HttpResponse

telephony_logger = logging.getLogger('telephony')


def app_login(request):

    if request.method == 'POST':
        if request.POST['username'] == '' or request.POST['password'] == '':
            return JsonResponse({"error": "Must enter username and password."})


        usernm = request.POST['username']
        passwd = request.POST['password']
        user = authenticate(username=usernm, password=passwd)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/dispatches/')
            else:
                # Return a 'disabled account' error message
                error = "Your account has been disabled."
                return JsonResponse({"error": error})
        else:
            # Return an 'invalid login' error message.
            error = "No user found with that username and password."
            return JsonResponse({"error": error})

    else:
        account_form = AccountForm()
        user_location_form = UserLocationForm()
        fixed_location_form = FixedLocationForm()

        structure_form = StructureForm()
        return render(request, 'global/public_auth.html', {"account_form": account_form,
                                                           "user_location_form": user_location_form,
                                                           "fixed_location_form": fixed_location_form,
                                                           "structure_form": structure_form})


class IsStaffOrTargetUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # allow user to list all users if logged in user is staff
        return view.action == 'retrieve' or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        # allow logged in user to view own details, allows staff to view all records
        return request.user.is_staff or obj == request.user


class AccountView(viewsets.ModelViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """
    serializer_class = AccountModelSerializer
    queryset = Account.objects.all()
    model = Account

    def get_permissions(self):
        # allow non-authenticated user to create via POST
        return (AllowAny() if self.request.method == 'POST'
                else IsStaffOrTargetUser()),


def logout_view(request):
    logout(request)
    return redirect('/dispatches/')


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
