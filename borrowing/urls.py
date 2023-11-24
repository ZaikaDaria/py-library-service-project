from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import BorrowingViewSet, ReturnBorrowingViewSet

router = DefaultRouter()
router.register("borrowings", BorrowingViewSet)

urlpatterns = [
    path(
        "api/borrowings/return/",
        ReturnBorrowingViewSet.as_view({"post": "create"}),
        name="return-borrowing",
    ),
] + router.urls

app_name = "borrowing"
