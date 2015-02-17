class Area(models.Model):
    owner = models.ForeignKey(User)
    world = models.ForeignKey(WorldBoundry)

class District(models.Model):
    area = models.ForeignKey(Area)
    
class ResponseArea(models.Model):
    district = models.ForeignKey(District)
    
class FixedLocation(models.Model):
    district = models.ForeignKey(District)
    lat = models.FloatField()
    lng = models.FloatField()
    street_address = models.CharField()
    district = models.ForeignKey(District)
    is_point = models.BooleanField(default=True)
    
    def nearest_hydrants(self):
        pass
    
    def nearest_firehouse(self):
        pass

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
    
    def nearest_hydrants(self):
        pass
        
     
class FireHouse(models.Model):
    structure = models.OnetoOneField(Structure)
    name = models.CharField()
    response_area = models.ForeignKey(ResponseArea)
    
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
    
    def get_coordinates(self):
      geo_str = " ".join(self.lat, self.lng)
      return geo_str
  
class DraftSite(models.Model):
    location = ForeignKey(FixedLocation) 
      