from collections import Counter
from datetime import datetime, timedelta
import getpass, os, email, sys, gmail, re, time, imaplib, string, pywapi
from httplib import HTTPResponse
import operator
import unicodedata
import urllib

from chartit import DataPool, Chart
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import json as simplejson
from map.models import Incident, FixedLocation, IncidentData
from map.views import compile_incident_location_string, geocode
from private.dispatch_settings import KEYS, DELINIATERS
from private.secret_settings import TWITTER_USERNAME, EMAIL_USERNAME
import simplejson


def incident_listener(request, source):
    pass
    
def parse_incident(payload):
    '''
    Using configurable incident data fields, parse the data into incident models with all of the information required.
    '''
    keys = set(KEYS)
    key_re = re.compile('(' + '|'.join(re.escape(key) for key in keys) + '):', re.IGNORECASE)
    key_locations = key_re.split(payload)[1:]
    incident_dict = {k: v.strip() for k,v in zip(key_locations[::2], key_locations[1::2])}
    
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
  
def normalize_incident_data(payload):
    '''
    Converts unicode data to a python string.
    '''
    payload = payload.replace('\n', '').replace('\r', '')
    try:
        payload =  unicodedata.normalize('NFKD', payload).encode('ascii', 'ignore') 
    except TypeError:
        #If this isn't unicode, and already a string
        pass
    
    return payload

def hippa_filter(payload):
    '''removes sensitive data early on'''
    pass

def process_import(incident_str, received_datetime):
    '''
    Manages the overall process of importing incidents.
    '''
    normalize = normalize_incident_data(incident_str)
    parse = parse_incident(normalize)
    incident_dict = parse
    loc_str = compile_incident_location_string(incident_dict)
    geo = geocode(loc_str)
    lat = geo[0]; lng = geo[1]
    fixed_loc = FixedLocation.objects.create(lat = lat, lng = lng, street_address=loc_str)
    incident = Incident.objects.create(payload=incident_str, location=fixed_loc, received_time = received_datetime)
    incident.save()
    for key, value in incident_dict.iteritems():
        incident_data = IncidentData.objects.create(incident=incident, key=key, value=value)
        incident_data.save()
    
    print "Created %d" % incident.id
    
    return HttpResponse(status=201)

def get_email_incidents(request, username):
    '''
    This view connects to an individuals gmail inbox, selects emails sent from 911 Dispatch,
    by sender address, and saves the emails to the databsse.
    '''
    usernm = raw_input("Username:")
    passwd = getpass.getpass(prompt='Password: ', stream=None)
    conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    conn.login(usernm,passwd)
    conn.select('Dispatch')

    #Only trying to parse the emails that are relevant. Selecting by sender and subject.
    typ, data = conn.search(None, '(FROM "messaging@iamresponding.com" SUBJECT "Company 43")')
    
    #Extract the data we need.
    for num in data[0].split():
        typ, msg_data = conn.fetch(num, '(RFC822)')
        for response_part in msg_data:
              if isinstance(response_part,tuple):
                  msg = email.message_from_string(response_part[1])
                  time_stamp = email.utils.parsedate(msg['Date'])
                  time_int = time.mktime(time_stamp)
                  received_datetime = datetime.fromtimestamp(time_int)
                  payload = msg.get_payload(decode=True)
                  process_import(payload, received_datetime)
                  
    return HttpResponse(status=201)


def get_twitter_incidents(twitter_username):
    '''
    Gathers statuses from a twitter feed.
    
    We expect that the status of each status is a sting in dictionary format
    containing the details of a 911 incident.
    
    Using application only authentication from the private module's tokens,
    attempt to retrieve as many statuses from one public twitter user as possible,
    using the public Twitter REST API.
    
    Save each status to the database along with it's publish time..
    '''
    api = TwitterAPI(settings.TWITTER_TOKEN_1, settings.TWITTER_TOKEN_2, settings.TWITTER_TOKEN_3, settings.TWITTER_TOKEN_4)
    r = api.request('statuses/user_timeline', {'screen_name':'%s' % twitter_username, \
                                               #We don't want anything except the statuses.
                                               'exclude_replies':'true', \
                                               # 3,200 is the TwitterAPI rate limit.
                                               'count': '3200', \
                                               #Further reduce our response size by excluding the user's metadata.
                                               'trim_user': 'true', \
                                               #Further reduce our response size by excluding other details
                                               'contributor_details': 'false', \
                                               #The ID of the oldest status to start importing from. 
                                               #This defaults to the oldest possible if the maximum rate limit is reached.
                                               'since_id': '' \
                                               })
    
    for status in r:
        received_datetime = datetime.strptime(status["created_at"], "%a %b %d %H:%M:%S +0000 %Y")
        status = status["text"]
        process_import(status, recieved_datetime)
        
    return HttpResponse(status=201)
    
    
    