import datetime

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from twisted.trial.unittest import TestCase

from apps.collect.views import process_import
from apps.map.models import *
from apps.people.models import Account
from collector.test_utils import FakeBulletin


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
        self.incident = process_import(FakeBulletin('good').generic(), datetime.datetime.now())

    def test_weather_snapshot_on_incident_meta_save(self):
        self.assertIsInstance(self.incident.meta.weather, WeatherSnapshot, 'Incident.meta does not contain weather object.')
