import json

import mock
from twisted.trial.unittest import TestCase
from twisted.internet import reactor
from apps.collect.client import handle_twitter_stream_event, stream_deferrer, process_import


class FakeTwitterStream(object):

    def __init__(self, condition='good'):
        self.condition = condition
        self.status_code = 200

    def iter_lines(self):
        if self.condition is 'bad':
            yield json.dumps({"text": "incident dict", "created_at": "July 2nd, 1983."})
        elif self.condition is 'good':
            with open('../sample_twitter_stream.txt', 'r') as f:
                yield f.readline()


class TwitterAPITestCase(TestCase):

    def test_incidentless_tweet_raises_geocoding_error(self):
        mock_tweet = FakeTwitterStream('bad').iter_lines().next()
        payload, dt = handle_twitter_stream_event(mock_tweet)
        self.assertRaises(ValueError, process_import, payload, dt)

    def test_stream_opens(self):
        sd = stream_deferrer(reactor, FakeTwitterStream())
        d = sd.next()
        return d
