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

def hydraulic_calculations(*args, **kwargs):
    '''
    perform fire flow mathematics
    '''
    pass

