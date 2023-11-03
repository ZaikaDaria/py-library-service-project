from rest_framework.response import Response
from rest_framework import status, viewsets
from .filters import BorrowingFilter
from .models import Borrowing
from .serializers import CreateBorrowingSerializer, BorrowingSerializer


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
