from django.test import TestCase
from store.serializers import BooksSerializer
from store.models import Book, UserBookRelation
from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg

class BookSerializerTestCase(TestCase):
    def test_ok(self):
        user1 = User.objects.create(username='user1', first_name="Ivan", last_name="Petrov")
        user2 = User.objects.create(username='user2', first_name="Ivan", last_name="Sidorov")
        user3 = User.objects.create(username='user3', first_name="1", last_name="2")

        book_1 = Book.objects.create(name='Test Book 1', price=25, author_name="Author 1", owner=user1)
        book_2 = Book.objects.create(name='Test Book 2', price=55, author_name="Author 1")

        UserBookRelation.objects.create(user=user1, book=book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user2, book=book_1, like=True, rate=5)
        user_book_3 = UserBookRelation.objects.create(user=user3, book=book_1, like=True)
        user_book_3.rate = 4
        user_book_3.save()

        UserBookRelation.objects.create(user=user1, book=book_2, like=True, rate=3)
        UserBookRelation.objects.create(user=user2, book=book_2, like=True, rate=4)
        UserBookRelation.objects.create(user=user3, book=book_2, like=False)

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))
        ).order_by('id')
        data = BooksSerializer(books, many=True).data
        expected_data = [
            {
                "id": book_1.id,
                "name": 'Test Book 1',
                "price": '25.00',
                "author_name": "Author 1",
                'annotated_likes': 3,
                'owner_name': 'user1',
                "rating": "5.00",
                'readers': [
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Petrov',
                    },
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Sidorov',
                    },
                    {
                        'first_name': '1',
                        'last_name': '2',
                    },
                ],
            },
            {
                "id": book_2.id,
                "name": 'Test Book 2',
                "price": '55.00',
                "author_name": "Author 1",
                'annotated_likes': 2,
                'owner_name': '',
                "rating": "3.50",
                'readers': [
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Petrov',
                    },
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Sidorov',
                    },
                    {
                        'first_name': '1',
                        'last_name': '2',
                    },
                ],
            },
        ]
        print(data)
        self.assertEqual(data, expected_data)
