import stripe
from datetime import datetime
from django.conf import settings

from borrowing.models import Borrowing
from payments.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_payment(borrowing: Borrowing, session: stripe.checkout.Session):
    total_price = borrowing.calculate_total_price()

    payment = Payment.objects.create(
        amount=total_price / 100,
        borrowing=borrowing,
        status="PENDING",
        quantity=1,
        created_at=datetime.utcfromtimestamp(session.created),
        session_url=session.url,
        session_id=session.id,
    )

    payment.session_url = session.url

    payment.session_id = session.id
    payment.save()

    return payment


def create_stripe_session(borrowing: Borrowing) -> stripe.checkout.Session:
    try:
        amount = int(100 * borrowing.book.fee * (borrowing.expected_return_date - borrowing.borrow_date).days)
        session = stripe.checkout.Session.create(
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": borrowing.book.title,
                    },
                    "unit_amount": amount,
                },
                "quantity": 1,
            }],
            mode="payments",
            success_url="http://127.0.0.1:8000/api/payments/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://127.0.0.1:8000/api/cancel",
        )
        create_payment(borrowing, session)
        return session

    except stripe.error.StripeError as e:
        print(f"Error creating Stripe Session: {str(e)}")
        return None
