from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BorrowingViewSet, ReturnBorrowingViewSet, PaymentViewSet

router = DefaultRouter()
router.register("borrowings", BorrowingViewSet)
router.register("payments", PaymentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/borrowings/return/', ReturnBorrowingViewSet.as_view({"post": "create"}), name="return-borrowing"),
]

app_name = "borrowing"
