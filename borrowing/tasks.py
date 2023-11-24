from celery import shared_task
from django.utils import timezone

from borrowing.models import Borrowing
from borrowing.telegram_notification import send_telegram_notification


@shared_task
def check_overdue_borrowings():
    today = timezone.now().date()
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=today,
        actual_return_date__isnull=True
    )

    if not overdue_borrowings:
        send_telegram_notification("No borrowings overdue today!")

    for borrowing in overdue_borrowings:
        message = f"Overdue borrowing: Book - {borrowing.book.title}, Borrower - {borrowing.user.username}"
        send_telegram_notification(message)
