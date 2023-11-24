from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import BorrowingViewSet

router = DefaultRouter()
router.register("borrowings", BorrowingViewSet)

urlpatterns = [
    path("", include(router.urls))
] + router.urls

app_name = "borrowing"
