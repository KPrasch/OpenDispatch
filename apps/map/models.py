from datetime import datetime
import re

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import *
from django.contrib.gis.measure import D
from django.db import models
from ast import literal_eval

#This must come last.
from django.contrib.gis.db import models


class InheritanceCastModel(models.Model):
    """
    An abstract base class that provides a ``real_type`` FK to ContentType.

    For use in trees of inherited models, to be able to downcast
    parent instances to their child types.

    """
    real_type = models.ForeignKey(ContentType, editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.real_type = self._get_real_type()
        super(InheritanceCastModel, self).save(*args, **kwargs)

    def _get_real_type(self):
        return ContentType.objects.get_for_model(type(self))

    def cast(self):
        return self.real_type.get_object_for_this_type(pk=self.pk)

    class Meta:
        abstract = True


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
    def __unicode__(self):
        return self.name

class Country(models.Model):
    world = models.ForeignKey(WorldBorder)
    name = models.CharField(max_length=24)
    code = models.CharField(max_length=30)
    poly = models.PolygonField()
    center = models.PointField()
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.name
    
class State(models.Model):
    country = models.ForeignKey(Country)
    name = models.CharField(max_length=24)
    code = models.CharField(max_length=2)
    poly = models.PolygonField()
    center = models.PointField()
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.name

class County(models.Model):
    state = models.ForeignKey(State)
    name = models.CharField(max_length=24)
    poly = models.PolygonField()
    center = models.PointField()
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.name
    
class Zipcode(models.Model):
    county = models.ForeignKey(County)
    code = models.CharField(max_length=5)
    poly = models.PolygonField()
    center = models.PointField()
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.name

class District(models.Model):
    zip = models.ForeignKey(Zipcode)
    name = models.CharField(max_length=24)
    poly = models.PolygonField()
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.name
    
class PrimaryResponseArea(models.Model):
    district = models.ForeignKey(District)
    name = models.CharField(max_length=24)
    center = models.PointField()
    poly = models.PolygonField()
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.name

#Areas of note within a Response Area
class TargetHazard(models.Model):
    response_area = models.ForeignKey(PrimaryResponseArea)
    name = models.CharField(max_length=24)
    center = models.PointField()
    poly = models.PolygonField()
    pts_of_interest = models.MultiPointField()
    description = models.CharField(max_length=400)
    hazmat = models.IntegerField()
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.name

class HeliSpot(models.Model):
    primary_response_area = models.ForeignKey(PrimaryResponseArea)
    name = models.CharField(max_length=24)
    center = models.PointField()
    poly = models.PolygonField()
    pts_of_interest = models.MultiPointField()
    description = models.CharField(max_length=100)
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.name
    
FIXED_LOCATIONS = []
    
    
#Points in Areas
class FixedLocation(models.Model):
    #response_area = models.ForeignKey(PrimaryResponseArea)
    type = models.IntegerField(choices = FIXED_LOCATIONS, blank=True, null=True)
    location = models.PointField()
    street_address = models.CharField(max_length=200)
    lat = models.FloatField()
    lng = models. FloatField()
    objects = models.GeoManager()

    def save(self, *args, **kwargs):
        self.location = Point(self.lat, self.lng)
        super(FixedLocation, self).save(*args, **kwargs) 
        
    def __unicode__(self):
        return '%s %d %d %r' % (self.street_address, self.location.x, self.location.y, self.location)
    
    def nearest_points(self):
        input_point = self.location
        distance = 2000 
        points = FixedLocation.objects.filter(location__distance_lte=(input_point, D(m=distance)))
        nearest_points = points.distance(input_point).order_by('distance')
        return nearest_points

class Incident(models.Model):
    #owner = models.ForeignKey(User)
    payload = models.CharField(max_length=10000, blank=True, null=True)
    location = models.ForeignKey(FixedLocation)
    is_active = models.BooleanField(default=False)
    annual_call_number = models.IntegerField(blank=True, null=True)
    dispatch_time = models.DateTimeField(blank=True, null=True)
    received_time = models.DateTimeField()
    created_time = models.DateTimeField(auto_now_add=True)
    weather_status = models.CharField(max_length=10000, blank=True, null=True)

    class Meta:
      unique_together = ["payload", "received_time"]
      ordering = ["received_time"] 
        
    def raw(self):
        return (literal_eval('%s' % self.payload))
    
    def time_str(self):
        return str(self.received_time)
    
    def loc(self):
        fixed_loc = self.location
        lat = self.location.location.x; lng = self.location.location.y
        return lat, lng
   
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
    
    def raw(self):
        return self.incident.id
    
CONSTRUCTION_CLASS = (
    ('1', 'Fire Resistive'),
    ('2', 'Non Combustible'),
    ('3', 'Ordinary'),
    ('4', 'Mill'),
    ('5', 'Wood Frame'),
)

class Structure(models.Model):
    location = models.ForeignKey(FixedLocation)  
    construction = models.IntegerField(choices=CONSTRUCTION_CLASS)
    stories = models.IntegerField()
    sq_ft = models.IntegerField()
    access_street = models.CharField(max_length=100)
    is_commercial = models.BooleanField(default=False)
    is_residential = models.BooleanField(default=False)
    has_sprinklers = models.BooleanField(default=False)
    fd_conn_loc = models.CharField(max_length=100)
    has_hazmat = models.BooleanField(default=False)
    has_preplan = models.BooleanField(default=False)
    preplan = models.TextField()
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.name
     
class FireHouse(models.Model):
    structure = models.ForeignKey(Structure)
    name = models.CharField(max_length=100)
    primary_response_area = models.ForeignKey(PrimaryResponseArea)
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.name
    
#Potential fire appliances to map
FIXED_APPLIANCES = (
    ('1', 'Hydrant'),
    ('2', 'Standpipe'),
    ('3', 'Sprinkler Control'),
    ('4', 'FD Connection'),
)

class FixedFireAppliance(models.Model):
    location = models.ForeignKey(FixedLocation)
    appliance = models.IntegerField(choices=FIXED_APPLIANCES)
    description = models.CharField(max_length=100)
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.name

#NFPA 2015 hydrant classification
NFPA_HYDRANT_CLASS = (
    ('1', 'AA'),
    ('2', 'B'),
    ('3', 'C'),
    ('4', 'D'),  
)

class Hydrant(models.Model):
    fixed_applicance = models.ForeignKey(FixedFireAppliance)
    nfpa_class = models.IntegerField(choices=NFPA_HYDRANT_CLASS)
    out_of_service = models.BooleanField(default=False)
    is_barell = models.BooleanField(default=True)
    is_wet = models.BooleanField(default=True)
    main_size_in = models.FloatField()
    sm_discharge_in = models.FloatField()
    lg_discharge_in = models.FloatField()
    thread_type = models.IntegerField()
    flow_test_date = models.DateTimeField(blank=True, null=True)
    exp_gpm = models.IntegerField()
    static_pressure = models.FloatField()
    flow_pressure = models.FloatField()
    resid_pressure = models.FloatField()
    objects = models.GeoManager()
  
    def __unicode__(self):
        return self.name
  
class DraftSite(models.Model):
    location = models.ForeignKey(FixedLocation) 
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.name
    
class Apparatus(models.Model):
    firehouse = models.ForeignKey(FireHouse)
    location = models.PointField(srid=4326)
    type = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)
    out_of_service = models.BooleanField(default=False)
    availible = models.BooleanField(default=True)
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.name
    
class Firefighter():
    pass

    def __unicode__(self):
        return self.name

    