from django.db import models
from borrowing.models import Borrowing

STATUS_CHOICES = [("PAID", "Payment Paid"), ("PENDING", "Payment Pending"), ("DENIED", "Payment Denies")]


class Payment(models.Model):
    borrowing = models.ForeignKey(Borrowing, on_delete=models.DO_NOTHING)
    status = models.CharField(choices=STATUS_CHOICES, max_length=7)
    session_url = models.URLField(max_length=255)
    session_id = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment ID: {self.id}, Amount: {self.amount}"
