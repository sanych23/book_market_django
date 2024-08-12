from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from store.serializers import BooksSerializer
from store.models import Book, UserBookRelation
from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.test.utils import CaptureQueriesContext
from django.db import connection
import json


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.book_1 = Book.objects.create(name='Test Book 1', price=25, author_name="Author 1", owner=self.user)
        self.book_2 = Book.objects.create(name='Test Book 2', price=55, author_name="Author 5")
        self.book_3 = Book.objects.create(name='Test Book Author 1', price=55, author_name="Author 2")
        UserBookRelation.objects.create(user=self.user, book=self.book_2, like=True, rate=3)

    def test_get(self):
        url = reverse('book-list')
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)
            self.assertEqual(2, len(queries))
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))
        ).order_by('id')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data[1]['rating'], "3.00")
        self.assertEqual(serializer_data[1]['annotated_likes'], 1)

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={"price":55})
        books = Book.objects.filter(id__in=[self.book_2.id, self.book_3.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))
        ).order_by('price')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'})
        books = Book.objects.filter(id__in=[self.book_1.id, self.book_3.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))
        )
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_get_order(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'price'})
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))
        ).order_by('id')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_get_one(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'id': self.book_1.id,
            'name': self.book_1.name,
            'price': '25.00',
            'author_name': self.book_1.author_name,
            'annotated_likes': 0,
            'rating': None,
            'owner_name': 'test_username',
            "readers": [],
        }
        self.client.force_login(self.user)
        response = self.client.get(url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, response.data)
    
    def test_create(self):
        self.assertEqual(Book.objects.all().count(), 3)
        url = reverse('book-list')
        data = {
            "name": "Python 3",
            "price": 150,
            "author_name": "Mark Summerfield",
            "owner": self.user.id,
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
            "author_name": "Mark Summerfield",
            "readers": [],
            'rating': None,
            'owner_name': 'test_username'
        }
        self.assertEqual(data, response.data)
        self.assertEqual(self.user, Book.objects.last().owner)


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

    def test_update_not_owner(self):
        self.user2 = User.objects.create(username='test_username2')
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 575,
            "author_name": self.book_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.book_1.refresh_from_db()
        self.assertEqual(25, self.book_1.price)

    def test_update_not_owner_but_staff(self):
        self.user2 = User.objects.create(username='test_username2', is_staff=True)
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 575,
            "author_name": self.book_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
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


class BooksRelationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.user2 = User.objects.create(username='test_username2')
        self.book_1 = Book.objects.create(name='Test Book 1', price=25, author_name="Author 1", owner=self.user)
        self.book_2 = Book.objects.create(name='Test Book 2', price=55, author_name="Author 5")

    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            "like": True,
        }
        json_data = json.dumps(data)

        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertTrue(relation.like)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            "rate": 3,
        }
        json_data = json.dumps(data)

        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertEqual(relation.rate, data["rate"])
        
    def test_rate_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            "rate": 6,
        }
        json_data = json.dumps(data)

        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
