import datetime
import json

from twisted.internet import reactor
from twisted.trial.unittest import TestCase

from apps.collect.incident import process_import
from collector.bulletin import BulletinTweet
from collector.client import store_stream
from collector.object_store_backend import COLLECTOR_BACKEND
from collector.test_utils import FakeBulletinFactory, FakeBulletinStream


class TwitterAPITestCase(TestCase):

    def setUp(self):
        self.fake_bulletin = FakeBulletinFactory(BulletinTweet, 'good')
        super(TwitterAPITestCase, self).setUp()

    def test_incidentless_tweet_raises_geocoding_error(self):
        fbf = FakeBulletinFactory(BulletinTweet, 'bad')
        tweet_bulletin = fbf.next()
        self.assertRaises(ValueError, process_import, tweet_bulletin)  # TODO: Decide if we want to test process_import at this stage.

    def test_tweet_is_pushed_to_backend(self):
        fbs = FakeBulletinStream('good')
        store_stream(reactor, fbs)
        tweet = COLLECTOR_BACKEND.pop()
        self.assertEqual(tweet, fbs.last_stream_item)

    def test_tweet_is_preprocessed(self):
        fbs = FakeBulletinStream('good')
        mock_tweet = fbs.iter_lines().next()
        tweet_bulletin = BulletinTweet(mock_tweet)
        event = json.loads(fbs.last_stream_item)
        self.assertEqual(event['text'], tweet_bulletin.payload)
        self.assertIsInstance(tweet_bulletin.received_dt, datetime.datetime)

