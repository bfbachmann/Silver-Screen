from django.test import TestCase, Client
from django.forms.forms import DeclarativeFieldsMetaclass
from app.models.models import *
from django.db import transaction

class TestRequests(TestCase):

    def test_valid_results_get_request(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get('/results/', {'query': 'Frozen'})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'], DeclarativeFieldsMetaclass))

    def test_valid_results_post_request(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post('/results/', {'query': 'Waterboy'})

        self.assertTrue(response.status_code == 200)
        self.assertEqual(response.context['query'], 'Waterboy')

    def test_invalid_results_request(self):
        client = Client(enforce_csrf_checks=True)
        response = client.patch('/results/', {'query': 'Waterboy'})

        self.assertTrue(response.status_code == 403)

    def test_index_get_request(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get('/index/')

        self.assertTrue(response.status_code == 200)
        self.assertTrue(isinstance(response.context['form'], QueryForm))

    def test_index_post_request(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post('/index/')

        self.assertTrue(response.status_code == 200)
        self.assertTrue(isinstance(response.context['form'], QueryForm))

    def test_invalid_index_request(self):
        client = Client(enforce_csrf_checks=True)
        response = client.patch('/index/')

        self.assertTrue(response.status_code == 403)

    def test_about_request(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get('/about/')

        self.assertTrue(response.status_code == 200)

    def test_overview_request(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get('/overview/')

        self.assertTrue(response.status_code == 200)
