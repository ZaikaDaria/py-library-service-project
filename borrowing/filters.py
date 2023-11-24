from django_filters import rest_framework as filters
from .models import Borrowing


class BorrowingFilter(filters.FilterSet):
    is_active = filters.BooleanFilter(field_name="actual_return_date", lookup_expr="isnull")
    user_id = filters.NumberFilter(field_name="user", method="filter_user_id")

    class Meta:
        model = Borrowing
        fields = ["is_active", "user_id"]

    def filter_user_id(self, queryset, name, value):
        if self.request.user.is_staff:
            if value is not None:
                return queryset.filter(user_id=value)
            return queryset
        return queryset.filter(user=self.request.user)
