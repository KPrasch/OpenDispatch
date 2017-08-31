import json
from datetime import datetime


class Incident(object):
    def __init__(self, unit, venue, incident, location, dispatch_time, additional=str()):
        self.unit = unit
        self.venue = venue
        self.incident = incident
        self.location = location
        self.dispatch_time = dispatch_time
        self.created = str(datetime.now())
        self.additional = additional
    
    def json(self):
        json_str = json.dumps(vars(self))
        return json_str

    def __repr__(self):
        r = f"{self.__class__.__name__}({self.unit}, {self.recieved})"
        return r