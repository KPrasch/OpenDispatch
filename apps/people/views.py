from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import redirect
from django.shortcuts import render
from apps.people.forms import AccountForm, UserForm, FixedLocationForm, UserLocationForm
from rest_framework.decorators import api_view, renderer_classes
from django.views.decorators.csrf import csrf_exempt


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
        return render(request, 'app/login.html', {"account_form": account_form,
                                                  "user_form": user_form,
                                                  "user_location_form": user_location_form,
                                                  "fixed_location_form": fixed_location_form})


def logout_view(request):
    logout(request)
    return redirect('/map/')

def registration(request):
    pass


