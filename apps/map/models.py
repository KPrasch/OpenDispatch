from datetime import datetime
import re

from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.db import models


#Areas
class WorldBorder(models.Model):
    # Regular Django fields corresponding to the attributes in the
    # world borders shapefile.
    name = models.CharField(max_length=50)
    area = models.IntegerField()
    pop2005 = models.IntegerField('Population 2005')
    fips = models.CharField('FIPS Code', max_length=2)
    iso2 = models.CharField('2 Digit ISO', max_length=2)
    iso3 = models.CharField('3 Digit ISO', max_length=3)
    un = models.IntegerField('United Nations Code')
    region = models.IntegerField('Region Code')
    subregion = models.IntegerField('Sub-Region Code')
    lon = models.FloatField()
    lat = models.FloatField()

    # GeoDjango-specific: a geometry field (MultiPolygonField), and
    # overriding the default manager with a GeoManager instance.
    mpoly = models.MultiPolygonField()
    objects = models.GeoManager()

    # Returns the string representation of the model.
    def __str__(self):              # __unicode__ on Python 2
        return self.name

class Country(models.Model):
    world = models.ForiegnKey(WorldBoundry)
    code = models.CharField(max_length=30)
    poly = models.PolygonField()
    objects = models.GeoManager()
    
class State(models.Model):
    country = models.ForiegnKey(County)
    code = models.CharField(max_length=2)
    poly = models.PolygonField()
    objects = models.GeoManager()

class County(models.Model):
    state = models.ForeignKey(State)
    owner = models.ForeignKey(User)
    world = models.ForeignKey(WorldBoundry)
    area = GeometryField()
    
class Zipcode(models.Model):
    county = models.ForiegnKey(County)
    code = models.CharField(max_length=5)
    poly = models.PolygonField()
    objects = models.GeoManager()

class District(models.Model):
    area = models.ForeignKey(Area)
    zip = models.ManytoManyField(Zipcode)
    objects = models.GeoManager()
    
class ResponseArea(models.Model):
    district = models.ForeignKey(District)
    objects = models.GeoManager()
    
class TargetHazard(models.Model):
    response_area = models.ForeignKey(ResponseArea)
    objects = models.GeoManager()
    
#Points in Areas
class FixedLocation(models.Model):
    company = models.ForeignKey(ResponseArea)
    location = models.PointField()
    lat = models.FloatField()
    lng = models.FloatField()
    street_address = models.CharField()
    district = models.ForeignKey(District)
    is_point = models.BooleanField(default=True)
    objects = models.GeoManager()
    
    def nearest_hydrants(self):
        pass
    
    def nearest_firehouse(self):
        pass
    
class Incident(models.Model):
    owner = models.ForeignKey(User)
    payload = models.CharField(max_length=10000, blank=True, null=True)
    lng = models.FloatField()
    lat = models.FloatField()
    zipcode= modelsIntegerField()
    is_active = models.BoleanField(default=False)
    annual_call_number = models.IntegerField()
    dispatch_time = models.DateTimeField(blank=True, null=True)
    recieved_time = models.DateTimeField(blank=True, null=True)
    created_time = models.DateTimeField(auto_add_now=True)
    #weather_status = IntegerField()
    
    class Meta:
      unique_together = ["payload", "datetime"]
      ordering = ["datetime"]
    
    def raw(self):
        return self.payload
    
    def geoloc(self):
        geo_loc = " ".join(self.lat, self.lng)
        return geo_loc
   
    def recieved_delay(self):
        if self.dispatch_time != self.recieved_time:
           delay = (self.dispatch_time-self.recieved_time).total_seconds()
           return delay
        else:
           return None
       
    def created_delay(self):
         if self.recieved_time != self.created_time:
           delay = (self.recieved_time-selfself.created_time).total_seconds()
           return delay
         else:
           return None
       
    def delay(self):
        rd = self.recieved_delay(self)
        cd = self.created_delay(self)
        if rd or cd is not None:
            print "delay detected %s %s" % rd, cd
            return rd, cd
        else:
            return False
            
class IncidentData(models.Model):
    incident = models.ForeignKey(Incident)
    key = models.CharField(max_length=200, blank=True)
    value = models.CharField(max_length=200, blank=True)
    
    def incident(self):
        return self.incident.id

class Structure(models.Model):
    location = models.ForeignKey(FixedLocation)  
    stories = models.IntegerField()
    sq_ft = models.IntegerField()
    access_street = models.CharField()
    is_commercial = models.BoleanField()
    is_residential = models.BoleanField
    has_sprinklers = models.BooleanField
    fd_conn_loc = models.CharField()
    has_hazmat = models.BoleanField()
    has_preplan = models.BooleanField()
    objects = models.GeoManager()
    
class Agency(models.Model):
    owner = models.ForeignKey(User)
    name = models.CharField()
     
class FireHouse(models.Model):
    structure = models.OnetoOneField(Structure)
    name = models.CharField()
    response_area = models.ForeignKey(ResponseArea)
    objects = models.GeoManager()
    
#Potential fire appliances to map
FIXED_APPLIANCES = (
    ('1', 'Hydrant'),
    ('2', 'Standpipe'),
    ('3', 'Sprinkler Control'),
    ('4', 'FD Connection'),
)

class FixedFireApplicance(models.Model):
    location = models.ForeignKey(FixedLocation)
    appliance = models.CharField(choices=FIXED_APPLIANCES)
    description = models.Charfield()
    objects = models.GeoManager()

#NFPA 2015 hydrant classification
NFPA_HYDRANT_CLASS = (
    ('AA', '> 1500 GPM'),
    ('A', '1000–1499 GPM'),
    ('B', '500–999 GPM'),
    ('C', '< 500 GPM'),  
)

class Hydrant(models.Model):
    fixed_applicance = models.ForeignKey(FixedFireAppliance)
    nfpa_class = models.CharField(choices=NFPA_HYDRANT_CLASS)
    out_of_service = models.BooleanFied(default=False)
    is_barell = models.BooleanField(default=True)
    is_wet = models.BooleanField()
    main_size_in = models.DecimalField()
    sm_discharge_in = models.DecimalField()
    lg_discharge_in = models.DecimalField()
    thread_type = models.IntegerField()
    flow_test_date = models.DateTimeField(blank=True, null=True)
    exp_gpm = models.IntegerField()
    static_pressure = models.FloatField()
    flow_pressure = models.FloatField()
    resid_pressure = models.FloatField()
    objects = models.GeoManager()
    
    def get_coordinates(self):
      geo_str = " ".join(self.lat, self.lng)
      return geo_str
  
class DraftSite(models.Model):
    location = ForeignKey(FixedLocation) 
    objects = models.GeoManager()
    
class Apparatus(models.Model):
    firehouse = models.ForiegnKey(FireHouse)
    type = models.CharField()
    capacity
    
    objects = models.GeoManager()
    
    
      