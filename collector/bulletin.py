from dateutil import parser
import json
import re
import logging

from apps.map.models import Fountain
from private.dispatch_settings import *

logger = logging.getLogger('django')


class BulletinBase(object):
    '''
    A short report, released by another party, which we believe includes details about one or more Incidents.
    '''
    @property
    def received_dt(self):
        return self._received_dt

    @property
    def payload(self):
        return self._payload

    @property
    def impetus(self):
        raise ValueError("impetus not available on BulletinBase.")

    def parse(self):
        """
        Using configurable incident data fields, parse the data into incident models with all of the information required.
        """

        keys = set(ESCAPE_KEYS)
        key_re = re.compile('(' + '|'.join(re.escape(key) for key in keys) + '):', re.IGNORECASE)
        key_locations = key_re.split(self.payload)[1:]
        bulletin_dictionary = {k: v.strip() for k, v in zip(key_locations[::2], key_locations[1::2])}

        return bulletin_dictionary


class StringBulletin(BulletinBase):

    def __init__(self, bulletin_string):
        super(StringBulletin, self).__init__()
        self._impetus = bulletin_string

    @property
    def impetus(self):
        return self._impetus


class BulletinTweet(StringBulletin):

    def __init__(self, bulletin_string, *args, **kwargs):
        super(BulletinTweet, self).__init__(bulletin_string, *args, **kwargs)
        self.stream_dict = json.loads(self.impetus)
        dt_string = self.stream_dict['created_at']
        self._received_dt = parser.parse(dt_string)
        self._payload = self.stream_dict["text"]

    @property
    def tweet_text(self):
        return self._payload

    @property
    def fountain(self):
        fountain = Fountain.objects.get(screen_name=self._payload["screen_name"])
        return fountain

    def parse(self):
        """
        Using configurable incident data fields, parse the data into incident models with all of the information required.
        """
        twitter_json = json.loads(self._payload)
        tweet = twitter_json["text"]
        keys = set(ESCAPE_KEYS)
        key_re = re.compile('(' + '|'.join(re.escape(key) for key in keys) + '):', re.IGNORECASE)
        key_locations = key_re.split(tweet)[1:]
        incident_dict = {k: v.strip() for k, v in zip(key_locations[::2], key_locations[1::2])}

        try:
            if twitter_json['screen_name'] is 'UlsterCounty911':
                regex = re.compile("([a-zA-Z_ ]*)([^a-zA-Z]*)$")
                s = regex.search(incident_dict["Venue"])

                if s.groups()[1] is not '':
                    # Adding a key to the dictionary here (dispatch time).
                    incident_dict['dispatch_time'] = parser.parse(s.groups()[1])
                    incident_dict['Venue'] = str.rstrip(s.groups()[0])

                    if "king" in incident_dict['Venue'].lower():
                        incident_dict["Venue"] = "Kingston"
                    elif "out of" in incident_dict["Venue"].lower():
                        incident_dict["Venue"] = ""
                        # Handle out of City Dispatches here.
                else:
                    regex = re.compile('[^a-zA-Z]')
                    incident_dict['Venue'] = str.rstrip(regex.sub(" ", incident_dict['Venue']))

        except KeyError:
            logger.warn("{0} does not exist in this bulletin".format(incident_dict))

        return incident_dict
