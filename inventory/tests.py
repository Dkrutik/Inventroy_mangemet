from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Item

class ItemTests(APITestCase):

    def test_create_item(self):
        url = reverse('create_item')
        data = {'name': 'Test', 'description': 'Test description',"quantity":79,"price":44444}
        response = self.client.post(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
