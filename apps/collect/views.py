from collections import Counter
from datetime import datetime, timedelta
import getpass, os, email, sys, gmail, re, time, imaplib, string, pywapi
from httplib import HTTPResponse
import operator
import urllib

from chartit import DataPool, Chart
from collect.email.models import IncidentEmail
import dispatch_settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import json as simplejson
from map.models import Incident
from private.dispatch_settings import KEYS, DELINIATOR
from private.secret_settings import TWITTER_USERNME, EMAIL_USERAME
import simplejson


def incident_listener(request, source):
    pass
    
def parse_incident(payload, sent):
    '''
    Using configurable incident data fields, parse the data into incident models with all of the information required.
    '''
    keys = set(KEYS)
    key_re = re.compile('(' + '|'.join(re.escape(key) for key in keys) + ')%r' % DELINIATER, re.IGNORECASE)
    key_locations = key_re.split(payload)[1:]
    incident_dict = {k: v.strip() for k,v in zip(key_locations[::2], key_locations[1::2])}
    # Create a model instance for each incident.
    return incident_dict

def import_incidents(request, source):
    '''
    Master incident import view.  Used for the initial population of the dispatch database.
    '''
    if source == 'twitter':
      get_twitter_incidents(request, TWITTER_USERNAME)
      return HTTPResponse(status=200)
    elif source == 'email':
      get_email_incidents(request, EMAIL_USERNAME)
      return HTTPResponse(status=200)
    else:
      raise ValueError("Invalid dispatch source.  Please specify twitter, email or cad.")  
  

def process_import(incident_str, received_datetime):
    '''
    Manages the overall process of importing incidents.
    '''
    normalize = normalize_incidnt_data(incident_str)
    parse = parse_incident(normalize.payload)
    incident_dict = parse.incident_dict
    loc_str = compile_incident_location_string(incident_dict)
    geocode = get_coordinates(loc_str.incident_location_string)
    lat = geocode.latitude; lng = geocode.longitude
    
    try: 
        incident = Incident.objects.create(recieved_datetime = recieved_datetime, lat = lat, lng = lng)
        incident.save()
    except ProgrammingError:
        pass

    for key,value in incident_dict:
        incident_data = IncidentData.objects.create(**locals())
        incident_data.save()
            
        print "Created Incident %d" % incident.id
        return HttpResponse(status=201)
    
    return HttpResponse(status=200)

def normalize_incident_data(payload):
    '''
    Converts unicode data to a python string.
    '''
    decoded_payload =  unicodedata.normalize('NFKD', payload).encode('ascii', 'ignore') 
    payload = decoded_payload.replace('\n', '').replace('\r', '')
    
    return payload

def hippa_filter(payload):
    '''removes sensitive data early on'''
    pass
    
    
    