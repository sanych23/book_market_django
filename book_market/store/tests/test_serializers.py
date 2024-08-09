from django.test import TestCase
from store.serializers import BooksSerializer
from store.models import Book
from django.contrib.auth.models import User

class BookSerializerTestCase(TestCase):
    def test_ok(self):
        owner = User.objects.create(username='test_username')
        book_1 = Book.objects.create(name='Test Book 1', price=25, author_name="Author 1", owner=owner)
        book_2 = Book.objects.create(name='Test Book 2', price=55, author_name="Author 1", owner=owner)
        data = BooksSerializer([book_1, book_2], many=True).data
        expected_data = [
            {
                "id": book_1.id,
                "name": 'Test Book 1',
                "price": '25.00',
                "author_name": "Author 1",
                "owner": book_1.owner.id,
            },
            {
                "id": book_2.id,
                "name": 'Test Book 2',
                "price": '55.00',
                "author_name": "Author 1",
                "owner": book_2.owner.id, 
            },
        ]
        self.assertEqual(data, expected_data)
