

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