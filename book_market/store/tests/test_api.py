from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from store.serializers import BooksSerializer
from store.models import Book
from django.contrib.auth.models import User
import json


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.book_1 = Book.objects.create(name='Test Book 1', price=25, author_name="Author 1")
        self.book_2 = Book.objects.create(name='Test Book 2', price=55, author_name="Author 5")
        self.book_3 = Book.objects.create(name='Test Book Author 1', price=55, author_name="Author 2")

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        serializer_data = BooksSerializer([self.book_1, self.book_2, self.book_3], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={"price":55})
        serializer_data = BooksSerializer([self.book_2, self.book_3], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'})
        serializer_data = BooksSerializer([self.book_1, self.book_3], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_get_order(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'price'})
        serializer_data = BooksSerializer([self.book_1, self.book_2, self.book_3], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_get_one(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'id': self.book_1.id,
            'name': self.book_1.name,
            'price': '25.00',
            'author_name': self.book_1.author_name
        }
        self.client.force_login(self.user)
        # self.assertEqual(Book.objects.all().count(), 3)
        response = self.client.get(url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, response.data)
    
    def test_create(self):
        self.assertEqual(Book.objects.all().count(), 3)
        url = reverse('book-list')
        data = {
            "name": "Python 3",
            "price": 150,
            "author_name": "Mark Summerfield"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.all().count(), 4)
        data = {
            "id": 4,
            "name": "Python 3",
            "price": '150.00',
            "author_name": "Mark Summerfield"
        }
        self.assertEqual(data, response.data)

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 575,
            "author_name": self.book_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book_1.refresh_from_db()
        self.assertEqual(575, self.book_1.price)

    def test_delete(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)
        self.assertEqual(Book.objects.all().count(), 3)
        response = self.client.delete(url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.all().count(), 2)
