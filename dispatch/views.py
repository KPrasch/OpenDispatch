from django.contrib import auth
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response


def login(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('templates/login.html', c)

def auth_view(request):
    username = request.POST.get('username', 'invalid_user')
    password = request.POST.get('password', 'invalid_pass')
    user = auth.authenticate(username=username, password=password)
    
    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect('%d/dashboard' % {{user.id}})
    else:
        return HttpResponseRedirect('accounts/invalid')

def logout(request):
    auth.logout(request)
    return render_to_response('accounts/logout')


def Dispatch(request, source):
    owner = models.ForeignKey(UserProfile)
    pass
    
def FireResponse(request):
    apparatus = models.ForeignKey(Apparatus)
    dispatch_time = models.DatetimeField()
    respond_time = models.DatetimeField()
    on_scene_time = models.DatetimeField()
    clear_time = models.DatetimeField()
    count = models.IntegerField()
    
    def save(*args, **kwargs):
        pass
    
    pass



    