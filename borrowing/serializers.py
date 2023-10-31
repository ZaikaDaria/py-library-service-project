from rest_framework import serializers
from borrowing.models import Borrowing, Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("title", "author")


class BorrowingSerializer(serializers.ModelSerializer):
    book_info = BookSerializer(source="book", read_only=True)

    class Meta:
        model = Borrowing
        fields = "__all__"
