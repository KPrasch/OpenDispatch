
def get_current_weather(zip):
    '''
    '''
    #Slightly more lacal.
    weather_com_result = pywapi.get_weather_from_weather_com(zip)
    yahoo_result = pywapi.get_weather_from_yahoo(zip)
    #Gather the bulk of the weather data from NOAA.
    noaa_result = pywapi.get_weather_from_noaa(dispatch_settings.NOAA_STATION_CALL_SIGN)
    

def get_historical_weather(request):
    pass