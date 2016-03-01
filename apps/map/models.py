import urllib

from django.contrib.gis.measure import D
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db import models

from apps.people.models import Account

import random
import hashlib


# Areas
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
    county = models.ForeignKey(County, related_name="zip_codes")
    code = models.CharField(max_length=5)
    poly = models.PolygonField()
    center = models.PointField()
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.name


class District(models.Model):
    zip = models.ForeignKey(Zipcode, related_name="districts")
    name = models.CharField(max_length=24)
    poly = models.PolygonField()
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.name


class PrimaryResponseArea(models.Model):
    district = models.ForeignKey(District, related_name="response_areas")
    name = models.CharField(max_length=24)
    center = models.PointField()
    poly = models.PolygonField()
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.name


# Areas of note within a Response Area
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


# Points in Areas
class FixedLocation(models.Model):
    # response_area = models.ForeignKey(PrimaryResponseArea)
    street_address = models.CharField(max_length=200)
    lat = models.FloatField()
    lng = models.FloatField()
    point = models.PointField(srid=4326)
    streetview_url = models.URLField(max_length=2000)

    def __str__(self):
        return "%.8f, %.8f, %s" % (self.lng, self.lat, self.street_address)
    
    def nearest_points(self):
        input_point = self.location
        distance = 2000 
        points = FixedLocation.objects.filter(location__distance_lte=(input_point, D(m=distance)))
        nearest_points = points.distance(input_point).order_by('distance')
        return nearest_points

    def save(self, *args, **kwargs):
        self.point = GEOSGeometry('{ "type": "Point", "coordinates": [%.8f, %.8f ]}' % (self.lng, self.lat))

        googleStreetviewUrl = 'https://maps.googleapis.com/maps/api/streetview?'
        params = {'location': self.street_address, 'sensor': "false",
                  'key': 'AIzaSyAY6BVObrWlkVMTYo5AqzlYcZf7SXChhg0', 'size': '600x300'}
        streetview_url = googleStreetviewUrl + urllib.urlencode(params)

        self.streetview_url = streetview_url
        super(FixedLocation, self).save(*args, **kwargs)


class Incident(models.Model):
    # owner = models.ForeignKey(User)
    payload = models.CharField(max_length=10000, editable=False)
    location = models.ForeignKey(FixedLocation)
    active = models.BooleanField(default=False)
    annual_call_number = models.IntegerField(blank=True, null=True)
    dispatch_time = models.DateTimeField(blank=True, null=True, editable=False)
    received_time = models.DateTimeField()
    created_time = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        unique_together = ["payload", "dispatch_time"]
        ordering = ["received_time"]
        
    def sms_str(self, user_location):
        greeting = "OpenDispatch Notification:"
        boilerplate = "near your %s at %s" % (user_location.category, user_location.poi.street_address)
        message = greeting + self.meta.dispatch + "\nwas dispatched to " + self.location.street_address + " \n" + boilerplate

        return message

    def raw(self):
        return self.payload
   
    def received_delay(self):
        if self.dispatch_time != self.received_time:
           delay = (self.dispatch_time-self.received_time).total_seconds()
           return delay
        else:
           return None
       
    def created_delay(self):
        if self.recieved_time != self.created_time:
            delay = (self.recieved_time-self.created_time).total_seconds()
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


class IncidentMeta(models.Model):
    incident = models.OneToOneField(Incident, related_name="meta")
    location = models.CharField(max_length=250)
    venue = models.CharField(max_length=250)
    dispatch = models.CharField(max_length=250)
    intersection = models.CharField(max_length=250)
    unit = models.CharField(max_length=250)

    def __unicode__(self):
        return str(self.incident.id)


class WeatherSnapshot(models.Model):
    incident = models.OneToOneField(IncidentMeta, related_name="weather")
    description = models.CharField(max_length=2000)
    station = models.CharField(max_length=200)
    wind_speed = models.FloatField()
    wind_heading = models.FloatField()
    rain = models.FloatField
    clouds = models.IntegerField
    temperature = models.FloatField()


CONSTRUCTION_CLASS = (
    ('1', 'Fire Resistive'),
    ('2', 'Non Combustible'),
    ('3', 'Ordinary'),
    ('4', 'Mill'),
    ('5', 'Wood Frame'),
    ('6', 'Unknown'),
)

BUILDING_TYPE = (
    ('Residence', 'Residence'),
    ('Commercial', 'Commercial'),
    ('Goverment', 'Goverment'),
    ('Industrial', 'Industrial'),
    ('Unknown', 'Unknown'),
)

FIXED_APPLIANCES = (
    ('1', 'Hydrant'),
    ('2', 'Standpipe'),
    ('3', 'Sprinkler Control'),
    ('4', 'FD Connection'),
)

# NFPA 2015 hydrant classification
NFPA_HYDRANT_CLASS = (
    ('1', 'AA'),
    ('2', 'B'),
    ('3', 'C'),
    ('4', 'D'),
)

TRUSSES = (
    ('IF', 'Type 1 Floor Truss'),
    ('IIF', 'Type 2 Floor Truss'),
    ('IIIF', 'Type 3 Floor Truss'),
    ('IVF', 'Type 4 Floor Truss'),
    ('VF', 'Type 5 Floor Truss'),
    ('IR', 'Type 1 Roof Truss'),
    ('IIR', 'Type 2 Roof Truss'),
    ('IIIR', 'Type 3 Roof Truss'),
    ('IVR', 'Type 4 Roof Truss'),
    ('VR', 'Type 5 Roof Truss'),
    ('IFR', 'Type 1 Floor and Roof Truss'),
    ('IIFR', 'Type 2 Floor and Roof Truss'),
    ('IIIFR', 'Type 3 Floor and Roof Truss'),
    ('IVFR', 'Type 4 Floor and Roof Truss'),
    ('VFR', 'Type 5 Floor and Roof Truss'),
)


class FixedFireAppliance(models.Model):
    location = models.ForeignKey(FixedLocation)
    appliance = models.IntegerField(choices=FIXED_APPLIANCES)
    description = models.CharField(max_length=100)
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.name


class Structure(models.Model):
    name = models.CharField(max_length=1500, blank=True, null=True)
    location = models.OneToOneField(FixedLocation)
    construction = models.IntegerField(choices=CONSTRUCTION_CLASS, blank=True, null=True, default='6')
    trusses = models.CharField(choices=TRUSSES, max_length=256, blank=True, null=True)
    regular_occupancy = models.PositiveIntegerField(blank=True, null=True)
    stories = models.IntegerField(blank=True, null=True)
    sqft = models.PositiveIntegerField(blank=True, null=True)
    access = models.TextField(blank=True, null=True)
    category = models.CharField(choices=BUILDING_TYPE, max_length=100, default='Unknown')
    sprinklers = models.BooleanField(default=False)
    additional = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name


def createUniqueKey():
        return hashlib.md5(str(random.randrange(1000000))).hexdigest()[0:7]


class Agency(models.Model):
    #owner = models.ForeignKey(UserProfile)
    name = models.CharField(max_length=100)
    unit = models.IntegerField()
    unique_id = models.CharField(max_length=8, default=createUniqueKey())

    def save(self, *args, **kwargs):
        # If agency doesn't exist in database, create a new random ID for it.
        if not self.pk:
            # This makes a unique id by truncating an MD5 hash of a random float between 0 and 1 million.
            key = createUniqueKey()
            # Ensure uniqueness.
            while Agency.objects.filter(unique_id=key).count() > 0:
                key = createUniqueKey()

            self.unique_id = key

        super(Agency, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name


HAZARDS = (
    ('Fuel', 'Fuel'),
    ('Chemicals', 'Chemicals'),
    ('None', 'None'),
    ('Unknown', 'Unknown'),
)

UTILITIES = (
    ('Heating', 'Heating'),
    ('Cooking', 'Cooking'),
    ('Electric', 'Electric'),
    ('Solar', 'Solar'),
    ('Water', 'Water'),
    ('Sewer', 'Sewer'),
    ('None', 'None'),
    ('Unknown', 'Unknown'),
)


class StructureHazard(models.Model):
    structure = models.ForeignKey(Structure, related_name="hazards")
    hazard = models.CharField(choices=HAZARDS, max_length=100, blank=True, null=True, default="Unknown")
    quantity = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=512, blank=True, null=True)


class StructureUtility(models.Model):
    structure = models.ForeignKey(Structure, related_name="utilities")
    utility = models.CharField(choices=UTILITIES, max_length=100, blank=True, null=True, default="Unknown")
    location = models.CharField(max_length=512, blank=True, null=True)
    provider = models.CharField(max_length=512, blank=True, null=True)
    notes = models.TextField(max_length=2000, blank=True, null=True)


class Station(Structure):
    description = models.CharField(max_length=100)
    agency = models.ForeignKey(Agency, related_name="stations")
    #primary_response_area = models.ForeignKey(PrimaryResponseArea)

    def __unicode__(self):
        return self.name


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
  
    def __unicode__(self):
        return self.name


class DraftSite(models.Model):
    location = models.ForeignKey(FixedLocation)
    access = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(max_length=2000)


USER_LOCATION_CATEGORIES = (
    ('Private Residence', 'Private Residence'),
    ('Shared Residence', 'Shared Residence'),
    ('Business', 'Business'),
    ('Commercial Structure', 'Commercial Structure'),
    ('Vacation Home', 'Vacation Home'),
    ('Apartments/Complex', 'Apartments/Complex'),
)


class UserLocation(models.Model):
    account = models.OneToOneField(Account)
    poi = models.OneToOneField(Structure)
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=512)
    category = models.CharField(choices=USER_LOCATION_CATEGORIES, max_length=256)

    def __unicode__(self):
        return self.title
