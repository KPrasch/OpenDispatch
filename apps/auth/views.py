from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import redirect
from django.shortcuts import render


def app_login(request):

    if request.method == 'POST':
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
        return render(request, 'app/login.html')


def logout_view(request):
    logout(request)
    return redirect('/map/')


