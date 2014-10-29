"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from Calendar.models import Request, Envs, Application


class EnvsTest(TestCase):
    def setUp(self):
	Application.objects.create(appname='ATLAS')
	Envs.objects.create(name='ENV6')
    def test_Env_creation(self):
        """
	Test that ENV6 is created
        """
	en = Envs.objects.get(name='ENV6')
        self.assertEqual(en.name, 'ENV6')
