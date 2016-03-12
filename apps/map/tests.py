from apps.collect.client import handle_twitter_stream_event, stream_twitter
from twisted.internet import defer
import mock
import json
from apps.collect.client import main
from twisted.internet import reactor
from twisted.trial.unittest import TestCase


class FakeTwitterStream(object):

    def iter_lines(self):
        yield json.dumps({"text": "incident dict", "created_at": "July 2nd, 1983."})


class TwitterAPITestCase(TestCase):

    def test_incidentless_tweet_raises_geocoding_error(self):
        mock_tweet = FakeTwitterStream().iter_lines().next()
        self.assertRaises(ValueError, handle_twitter_stream_event, mock_tweet)


    @mock.patch('requests.get')
    def test_stream_opens(self, mock_request):
        mock_request.return_value = FakeTwitterStream()
        stream_iterator = main(reactor)
        md = defer.maybeDeferred(stream_iterator.next)
        self.fail()
