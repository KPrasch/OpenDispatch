from datetime import datetime
import re

from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelForm
from gi.overrides.GLib import Source
from numpy.distutils.exec_command import temp_file_name
from reportlab.lib.colors import snow
from PIL.ImageDraw import floodfill

    
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
    
    
class IncidentWeatherData(models.Model):
    incident = models.ForeignKey(Incident)
    observation_time
    observation_loc
    observation_lat
    observation_lng
    
#class IncidentHazardCondition(models.Model):

#class IncidentExistingWeatherCondition(models.Model):
    
#class IncidentFutureConditions(models.Model):

class IncidentTemp(models.Model):
    incident_weather_data = models.ForeignKey(IncidentWeatherData)
    temp_f = models.DecimalField()
    temp_c = models.DecimalField()

class IncidentWind(models.Model):
    incident_weather_data = models.ForeignKey(IncidentWeatherData)
    wind_speed_mph = models.DecimalField()
    wind_heading = models.IntegerField()
    wind_chill_f = models.IntegerField()
    wind_chill_c = models.IntegerField()
    wind_gust_mph = models.DecimalField()
    
class IncidentPercipitation(models.Model):
    incident_weather_data = models.ForeignKey(IncidentWeatherData)
    rain
    snow
    mixture
    
    
class IncidentDewPoint(models.Model):
    incident_weather_data = models.ForeignKey(IncidentWeatherData)

class IncidentPressure(models.Model):
    incident_weather_data = models.ForeignKey(IncidentWeatherData)
    pressure_mb






    
    
        
    
    

