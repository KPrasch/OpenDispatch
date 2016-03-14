import datetime
import json

from twisted.internet import reactor
from twisted.trial.unittest import TestCase

from apps.collect.views import process_import
from collector.bulletin import BulletinTweet
from collector.client import store_stream
from collector.object_store_backend import COLLECTOR_BACKEND
from collector.test_utils import FakeBulletin


class TwitterAPITestCase(TestCase):

    def setUp(self):
        self.fake_bulletin = FakeBulletin('good').twitter()
        super(TwitterAPITestCase, self).setUp()

    def test_incidentless_tweet_raises_geocoding_error(self):
        self.fake_bulletin = FakeBulletin('bad').twitter()
        mock_tweet = self.fake_bulletin.iter_lines().next()
        tweet_bulletin = BulletinTweet(mock_tweet)
        self.assertRaises(ValueError, process_import, tweet_bulletin)  # TODO: Decide if we want to test process_import at this stage.

    def test_tweet_is_pushed_to_backend(self):
        fts = FakeBulletin('good').twitter()
        store_stream(reactor, fts)
        tweet = COLLECTOR_BACKEND.pop()
        self.assertEqual(tweet, fts.last_stream_item)

    def test_tweet_is_preprocessed(self):
        self.fake_bulletin = FakeBulletin('good').twitter()
        mock_tweet = self.fake_bulletin.iter_lines().next()
        tweet_bulletin = BulletinTweet(mock_tweet)
        event = json.loads(self.fake_bulletin.last_stream_item)
        self.assertEqual(event['text'], tweet_bulletin.payload)
        self.assertIsInstance(tweet_bulletin.received_dt, datetime.datetime)

