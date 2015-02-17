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