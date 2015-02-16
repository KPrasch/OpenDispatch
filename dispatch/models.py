from datetime import datetime
import re

from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelForm
from gi.overrides.GLib import Source
from numpy.distutils.exec_command import temp_file_name
from reportlab.lib.colors import snow
from PIL.ImageDraw import floodfill
from gettext import lngettext
from openshot.uploads.youtube.gdata.youtube import Company

    
class Incident(models.Model):
    owner = models.ForeignKey(User)
    payload = models.CharField(max_length=10000, blank=True, null=True)
    lng = models.DecimalField(max_digits=50, decimal_places=1, null= True, blank=True)
    lat = models.DecimalField(max_digits=50, decimal_places=1, null= True, blank=True)
    #zipcode= modelsIntegerField()
    dispatch_time = models.DateTimeField(blank=True, null=True)
    recieved_time = models.DateTimeField(blank=True, null=True)
    created_time = models.DateTimeField(auto_add_now=True)
    #weather_status = IntegerField()
    
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
       
    def time_disparity(self):
        rd = self.recieved_delay(self)
        cd = self.created_delay(self)
        if rd or cd is not None:
            return True
        else:
            return False
               
    class Meta:
      unique_together = ["payload", "datetime"]
      order_by = ["datetime"]
      
class IncidentData(models.Model):
    incident = models.ForeignKey(Incident)
    key = models.CharField(max_length=200, blank=True)
    value = models.CharField(max_length=200, blank=True)
    
    def incident(self):
        return self.incident.id
    
#class FixedFireApplicance(models.Model):

NFPA_class = ['1', 'Class A', '2', 'Class A', '3', 'Class A', '4', 'Class A', '5', 'Class A', ]
paint_color = []

class Hydrant(models.Model):
    lat = models.DecimalField()
    lng = models.DecimalField()
    street_address = models.CharField()
    NFPA_class = models.IntegerField()
    paint_color = models.IntegerField()
    wet_or_dry = models.BooleanField
    main_size_in = models.DecimalField()
    sm_discharge_in = models.DecimalField()
    lg_discharge_in = models.DecimalField()
    thread_type = models.IntegerField()
    flow_test_date = models.DateTimeField(blank=True, null=True)
    exp_gpm = models.IntegerField()
    static_pressure = models.DecimalField()
    resid_pressure = models.DecimalField()
    
    def get_coordinates(self):
      geo_str = " ".join(self.lat, self.lng)
      return geo_str

    







    
    
        
    
    

