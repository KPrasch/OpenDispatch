import json

import datetime
from twisted.trial.unittest import TestCase as TwistedTestCase
from django.test import TestCase
from twisted.internet import reactor
from apps.collect.client import handle_twitter_stream_event, stream_deferrer, process_import

from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.map.models import *
from apps.people.models import Account

class FakeTwitterStream(object):

    def __init__(self, bulliten, condition='good'):
        self.condition = condition
        self.status_code = 200
        self.last_stream_item = bulliten

    def iter_lines(self):
        yield self.last_stream_item


class FakeBulliten(object):

    def __init__(self, condition='good'):
        if condition is 'good':
            with open('../sample_twitter_stream.txt', 'r') as f:
                self.bulliten = f.readline()

        elif condition is 'bad':
            self.bulliten = json.dumps({"text": "incident dict", "created_at": "July 2nd, 1983."})

        elif condition is 'alright':
            self.bulliten = json.dumps({"text": "incident dict", "created_at": "November, 8th, 1990"})

    def twitter(self):
        return FakeTwitterStream(self.bulliten)

    def generic(self):
        return json.loads(self.bulliten)['text']


class TwitterAPITestCase(TwistedTestCase):

    def setUp(self):
        self.fake_bulliten = FakeBulliten('good').twitter()
        super(TwitterAPITestCase, self).setUp()

    def test_incidentless_tweet_raises_geocoding_error(self):
        self.fake_bulliten = FakeBulliten('bad').twitter()
        mock_tweet = self.fake_bulliten.iter_lines().next()
        payload, dt = handle_twitter_stream_event(mock_tweet)
        self.assertRaises(ValueError, process_import, payload, dt)

    def test_twitter_stream_handler(self):
        fts = self.fake_bulliten
        sd = stream_deferrer(reactor, fts)
        d = sd.next()

        def analyze_stream(stream_data, test_case, fts):
            payload, dt = stream_data
            event = json.loads(fts.last_stream_item)
            test_case.assertEqual(event['text'], payload)
            test_case.assertIsInstance(dt, datetime.datetime)

        d.addCallback(analyze_stream, self, fts)
        return d


class AccountTests(APITestCase):
    client = APIClient()

    def test_create_account(self):
        """
        Ensure we can create a new account object.
        """
        url = '/api/accounts/'
        data = {'email': 'test@test.com', 'first_name': 'Test', 'last_name': 'Testerson', 'username': 'TestTesterson', 'password': 'insecure'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Account.objects.count(), 1)
        self.assertEqual(Account.objects.get().email, 'test@test.com')


class IncidentTests(TestCase):
    def setUp(self):
        self.incident = process_import(FakeBulliten('good').generic(), datetime.datetime.now())

    def test_weather_snapshot_on_incident_meta_save(self):
        self.assertIsInstance(self.incident.meta.weather, WeatherSnapshot, 'Incident.meta does not contain weather object.')