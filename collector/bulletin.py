from dateutil import parser
import json


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