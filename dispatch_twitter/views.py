from collections import Counter
from datetime import datetime, timedelta
import getpass, os, email, sys, gmail, dispatch_gmail, re, time, imaplib, string, pywapi
import operator
import unicodedata

from TwitterAPI import TwitterAPI
from chartit import DataPool, Chart
from dispatch.models import UlsterIncident
from dispatch.views import parse_incident
from dispatch_gmail.models import IncidentEmail
from dispatch_twitter.models import TwitterIncident
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import json as simplejson
from private import local-settings

def import_twitter_incidents(request):
    '''
    '''
    api = TwitterAPI(settings.TWITTER_TOKEN_1, settings.TWITTER_TOKEN_2, settings.TWITTER_TOKEN_3, settings.TWITTER_TOKEN_4)
    r = api.request('statuses/user_timeline', {'screen_name':'ulstercounty911', \
                                               'exclude_replies':'true', \
                                               'count': '3200', \
                                               })
    
    for status in r:
        received_datetime = datetime.strptime(status["created_at"], "%a %b %d %H:%M:%S +0000 %Y")
        normalized_data =  unicodedata.normalize('NFKD', status["text"]).encode('ascii', 'ignore') 
        payload = normalized_data.replace('\n', '').replace('\r', '')
        twitter_incident = TwitterIncident.objects.create(datetime = received_datetime, payload = payload)
        twitter_incident.save()
        sys.stdout.write("Saved twitter dispatch %s \r" % twitter_incident.id)
        sys.stdout.flush()
        parse_incident(payload, received_datetime)
    print "Done."
    return render(request, 'dashboard.html')
