from django.test import TestCase
from store.logic import operation


class LogicTestCase(TestCase):
    def test_plus(self):
        result = operation(6, 13, "+")
        self.assertEqual(19, result)

    def test_minus(self):
        result = operation(2, 2, "-")
        self.assertEqual(0, result)

    def test_multiply(self):
        result = operation(2, 2, "*")
        self.assertEqual(4, result)

    def test_delenie(self):
        result = operation(5, 1, "/")
        self.assertEqual(5, result)
