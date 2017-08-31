"""
Incident processing pipeline functions

"""

import threading
from _datetime import datetime

from consumers.parsers import process_incident
from publishers.twitter import stream as twitter_stream
from router import adapter_selector


class IncidentBuffer(object):
    def __init__(self):
        self.incidents = list()

    def put(self, data, source, agency):
        payload = {'recieved': datetime.now(), 'agency': agency, 'source': source, 'payload': data}
        self.incidents.append(payload)

    def get(self):
        return self.incidents.pop(0)

    def __len__(self):
        return len(self.incidents)


class IncidentCollector(object):
    def __init__(self):
        self.created = datetime.now()
        self.buffer = IncidentBuffer()
        self.tpool = list()

    def start(self):
        print("Starting Up")
        self.collect()
        self.process()

    def collect(self):
        """Populates Incident Queue"""
        sources = [twitter_stream, ]
        for source in sources:
            t = threading.Thread(target=source, args=(self,), daemon=True)
            t.start()
            self.tpool.append(t)

    def process(self):
        """Processes incident Queue"""
        while True:
            # Incoming incident data pipeline
            if len(self.buffer) > 0:                         # If there is an incident on the stack
                incident_data = self.buffer.get()            # Retrieve an incident off the stack
                self.worker(incident_data)

    def worker(self, incident_data):
        """Parsing and broadcasting pipeline: outbound"""
        adapter = adapter_selector(incident_data)            # Inspect the incident, and choose its incident adapter
        incident_dict = adapter(incident_data)               # Invoke the incident adapter; Parse the incident to dict
        incident = process_incident(incident_dict)           # Create an Incident

        # Send to Collector and Broadcaster
        # broadcast_incident(incident)
        # collect_incident(incident)
