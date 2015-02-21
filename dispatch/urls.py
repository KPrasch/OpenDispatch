from django.conf.urls import patterns, include, url
from django.contrib import admin
from dispatch_gmail import views
from dispatch_twitter import views

admin.autodiscover()

urlpatterns = patterns('',
                       
    #Forward facing URLs
    url(r'^$', 'main.views.main', name='home'),
                       
    #Authentication                   
    url(r'^/accounts/login/$', 'dispatch.views.login'),
    url(r'^/accounts/logout/$', 'dispatch.views.logout'),
    url(r'^/accounts/invalid/$', 'dispatch.views.invalid_login'),
    
    #User Interface
    url(r'^/dashboard', 'dispatch.views.dasboardView', name='dashboard'),
    url(r'^settings', 'dispatch.views.settingsView', name='settings'),
    url(r'^incidents', 'dispatch.views.incidentsView', name='incidents'),
    url(r'^map', 'map.views.mapView', name='map'),
    url(r'^chart', 'chart.views.chartView', name='chart'),
    url(r'^board', 'respond.views.respondView', name='board'),

    #Incident db population
    url(r'^import-email/', 'dispatch_gmail.views.import_email_incidents'),
    url(r'^import-twitter/', 'dispatch_twitter.views.import_twitter_incidents'),


)
