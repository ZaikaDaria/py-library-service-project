from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status, viewsets
from borrowing.filters import BorrowingFilter
from borrowing.models import Borrowing
from borrowing.serializers import CreateBorrowingSerializer, BorrowingSerializer, PaymentSerializer


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


class ReturnBorrowingViewSet(viewsets.ViewSet):
    def create(self, request, *args, **kwargs):
        borrowing_id = request.data.get("borrowing_id")
        try:
            borrowing = Borrowing.objects.get(id=borrowing_id)
        except Borrowing.DoesNotExist:
            return Response({"detail": "Borrowing not found"}, status=status.HTTP_404_NOT_FOUND)

        if borrowing.actual_return_date:
            return Response({"detail": "Borrowing has already been returned"}, status=status.HTTP_400_BAD_REQUEST)

        borrowing.actual_return_date = timezone.now()
        borrowing.save()

        # Increase book inventory by 1
        borrowing.book.inventory += 1
        borrowing.book.save()

        serializer = BorrowingSerializer(borrowing)
        return Response(serializer.data, status=status.HTTP_200_OK)
