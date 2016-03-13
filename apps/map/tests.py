from apps.collect.client import handle_twitter_stream_event, stream_twitter
from apps.map.sample_twitter_stream_data import sample_twitter_stream_string
from twisted.internet import defer
import mock
import json
from apps.collect.client import main
from twisted.internet import reactor
from twisted.trial.unittest import TestCase


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
        self.assertRaises(ValueError, handle_twitter_stream_event, mock_tweet)

    @mock.patch('requests.get')
    def test_stream_opens(self, mock_request):
        mock_request.return_value = FakeTwitterStream()
        stream_iterator = main(reactor)
        d = stream_iterator.next()
        return d
