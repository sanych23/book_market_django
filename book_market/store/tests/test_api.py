from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from store.serializers import BooksSerializer
from store.models import Book


class BooksApiTestCase(APITestCase):
    def test_get(self):
        book_1 = Book.objects.create(name='Test Book 1', price=25)
        book_2 = Book.objects.create(name='Test Book 2', price=25)
        url = reverse('book-list')
        response = self.client.get(url)
        serializer_data = BooksSerializer([book_1, book_2], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)
