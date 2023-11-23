from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import Borrowing, Book
from .serializers import BorrowingSerializer, CreateBorrowingSerializer
from decimal import Decimal
from datetime import date, timedelta


class BorrowingViewSetTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.author = User.objects.create_user(username="author", password="password")
        self.cover_image_path = "/path/to/your/image.jpg"
        self.cover_image = SimpleUploadedFile(
            "cover.jpg", open(self.cover_image_path, "rb").read()
        )
        self.book = Book.objects.create(
            title="Test Book",
            author=self.author,
            cover=self.cover_image,
            inventory=10,
            daily_fee=Decimal("1.99"),
            price=Decimal("19.99"),
        )

        self.client = APIClient()

    def test_create_borrowing(self):
        url = reverse("borrowing-list")
        data = {
            "user": self.user.id,
            "book": self.book.id,
            "borrow_date": date.today(),
            "expected_return_date": date.today() + timedelta(days=14),
            "actual_return_date": None,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)

        borrowing = Borrowing.objects.get(pk=response.data["id"])
        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(borrowing.book, self.book)
        self.assertEqual(borrowing.borrow_date, data["borrow_date"])
        self.assertEqual(borrowing.expected_return_date, data["expected_return_date"])
        self.assertEqual(borrowing.actual_return_date, data["actual_return_date"])

    def test_cancel_borrowing(self):
        url = reverse("borrowing-cancel", args=[self.borrowing.pk])

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("success", response.data)
        self.assertIn("message", response.data)

    def test_return_borrowing(self):
        url = reverse("borrowing-return_borrowing", args=[self.borrowing.pk])

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

        self.borrowing.refresh_from_db()

        self.assertTrue(self.borrowing.actual_return_date)
        self.assertEqual(self.borrowing.book.inventory, self.initial_inventory + 1)

    def tearDown(self):
        self.borrowing.delete()
        self.user.delete()
        self.book.delete()
        self.author.delete()
