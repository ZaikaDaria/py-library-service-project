from book_service.models import Book
from django.db import models


class Borrowing(models.Model):
    user = models.ForeignKey("user.User", on_delete=models.DO_NOTHING, related_name="borrowings")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)

    def calculate_total_price(self):
        if self.book:
            return self.book.price
        return 0
