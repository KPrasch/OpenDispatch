from collections import Counter
from datetime import datetime, timedelta
import getpass, os, email, sys, gmail, dispatch_gmail, re, time, imaplib, string, pywapi
from httplib import HTTPResponse
import operator
import pdb
import urllib

from chartit import DataPool, Chart
from dispatch.models import UlsterIncident
from dispatch_gmail.models import IncidentEmail
import dispatch_settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import json as simplejson
import simplejson

def incident_listener(request, source):
    pass
    
def parse_incident(payload, sent):
    '''
    Take an incident string and make a dictionary. Needs refactor for the alternate schema.
    '''
    broken = payload.split(':')
    key_re = re.compile('(' + '|'.join(re.escape(key) for key in keys) + ')%r' % dispatch_settings.DELINIATER, re.IGNORECASE)
    key_locations = key_re.split(payload)[1:]
    incident_dict = {k: v.strip() for k,v in zip(key_locations[::2], key_locations[1::2])}
    
    return incident_dict

def import_incidents(request, source):
    '''
    Master incident import view.  Used for the initial population of the dispatch database.
    '''
    if source == 'twitter':
      get_twitter_incidents(dispatch_settings.TWITTER_USERNAME)
      return HTTPResponse(status=200)
    elif source == 'email':
      get_email_incidents(dispatch_settings.EMAIL_USERNAME)
      return HTTPResponse(status=200)
    else:
      raise ValueError("Invalid dispatch source.  Please specify twitter, email or cad.")  
  

def process_import(incident_str, recieved_datetime):
    '''
    Manages the overall process of importing incidents.
    '''
    normalize = normalize_incidnt_data(incident_str)
    parse = parse_incident(normalize.payload)
    incident_dict = parse.incident_dict
    loc_str = incident_location_string(incident_dict)
    geocode = get_coordinates(loc_str.incident_location_string)
    lat = geocode[0]; lng = geocode[1]
    
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