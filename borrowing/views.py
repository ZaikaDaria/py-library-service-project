import stripe

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets

from borrowing.filters import BorrowingFilter
from borrowing.models import Borrowing
from borrowing.serializers import CreateBorrowingSerializer, BorrowingSerializer
from library.settings import STRIPE_SECRET_KEY
from payments.models import Payment
from payments.sessions import create_stripe_session

stripe.api_key = STRIPE_SECRET_KEY

FINE_MULTIPLIER = 2
DAILY_FEE = 1.5


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    filter_class = BorrowingFilter

    def create(self, request, *args, **kwargs):
        serializer = CreateBorrowingSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        if self.request.user.is_staff:
            return Borrowing.objects.all()
        return Borrowing.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def cancel_action(self, request, pk=None):
        borrowing = get_object_or_404(Borrowing, pk=pk)

        try:
            cancel_endpoint = reverse("borrowing:cancel-action", kwargs={"pk": borrowing.pk})
            absolute_cancel_url = request.build_absolute_uri(cancel_endpoint)
            return JsonResponse({"success": True,
                                 "message": f"Payment can be paid a bit later. Session available for 24h. Cancel URL: {absolute_cancel_url}"})
        except stripe.error.StripeError as e:
            print(f"Error retrieving Stripe Session: {str(e)}")
            return JsonResponse({"success": False, "message": "Error retrieving Stripe Session"})


class ReturnBorrowingViewSet(viewsets.ViewSet):
    def create(self, request, *args, **kwargs):
        borrowing_id = request.data.get("borrowing_id")
        try:
            borrowing = Borrowing.objects.get(id=borrowing_id)
        except Borrowing.DoesNotExist:
            return Response({"detail": "Borrowing not found"}, status=status.HTTP_404_NOT_FOUND)

        if borrowing.is_overdue:
            days_overdue = (borrowing.actual_return_date - borrowing.expected_return_date).days
            fine_amount = days_overdue * DAILY_FEE * FINE_MULTIPLIER

            fine_payment = Payment.objects.create(
                borrowing=borrowing,
                amount=fine_amount,
                paid=False
            )
            stripe_session_id = create_stripe_session(fine_payment)

            if stripe_session_id:
                print(f"Fine Payment created successfully for Borrowing ID {borrowing.id}")
                return Response(
                    {'message': 'Fine payment created successfully.', 'stripe_session_id': stripe_session_id})
            else:
                print(f"Failed to create Fine Payment for Borrowing ID {borrowing.id}")
                return Response({'error': 'Failed to create Fine Payment'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if borrowing.actual_return_date:
            return Response({"detail": "Borrowing has already been returned"}, status=status.HTTP_400_BAD_REQUEST)

        borrowing.actual_return_date = timezone.now()
        borrowing.save()

        borrowing.book.inventory += 1
        borrowing.book.save()

        serializer = BorrowingSerializer(borrowing)
        return Response(serializer.data, status=status.HTTP_200_OK)
