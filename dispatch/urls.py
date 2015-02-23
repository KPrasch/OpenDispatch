from django.conf.urls import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
                       
    #Forward facing URLs
    url(r'^$', 'public.views.main', name='home'),
                       
    #Authentication                   
    url(r'^/accounts/login/$', 'dispatch.views.login'),
    url(r'^/accounts/logout/$', 'dispatch.views.logout'),
    url(r'^/accounts/invalid/$', 'dispatch.views.invalid_login'),
    
    #User Interface
    url(r'^dashboard/$', 'dispatch.views.dashboard', name='dashboard'),
    url(r'^settings/$', 'dispatch.views.settingsView', name='settings'),
    url(r'^incidents/$', 'dispatch.views.incidentsView', name='incidents'),
    url(r'^map/$', 'map.views.mapView', name='mapView'),
    url(r'^chart/$', 'chart.views.chartView', name='chart'),
    url(r'^board/$', 'respond.views.respondView', name='board'),

    #Incident db population
    url(r'^import/(?P<source>\w{0,50})/$', 'collect.views.import_incidents'),


)
