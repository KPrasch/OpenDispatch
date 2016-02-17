from django.test import TestCase
import unittest
from django.test.client import Client


def test_200_on_map(self):
    c = Client()
    response = c.post('/dispatches')

    self.assertEual(response.status_code, 200)