from rest_framework import serializers
from borrowing.models import Borrowing, Book
from borrowing.telegram_notification import send_telegram_notification


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("title", "author")


class BorrowingSerializer(serializers.ModelSerializer):
    book_info = BookSerializer(source="book", read_only=True)

    class Meta:
        model = Borrowing
        fields = "__all__"


class CreateBorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ('book', 'borrow_date', 'expected_return_date')

    @staticmethod
    def validated_book(book):
        if book.inventory <= 0:
            raise serializers.ValidationError("Book is out of stock.")
        return book

    def create(self, validated_data):
        user = self.context['request'].user
        borrowing = Borrowing.objects.create(user=user, **validated_data)

        book = validated_data['book']
        book.inventory -= 1
        book.save()
        message = f"New borrowing created: Book - {book.title}, Borrower - {user.username}"
        send_telegram_notification(message)

        return borrowing
