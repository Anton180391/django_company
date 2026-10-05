from datetime import timedelta

import django_filters as filters
from django.utils import timezone

from .models import Employee


class EmployeeFilter(filters.FilterSet):
    """Фильтрация сотрудников по навыкам и стажу."""

    skill = filters.CharFilter(
        field_name="skill_levels__skill__name",
        lookup_expr="icontains",
        label="Навык",
    )
    min_experience_days = filters.NumberFilter(
        method="filter_min_experience",
        label="Минимальный стаж (дней)",
    )
    max_experience_days = filters.NumberFilter(
        method="filter_max_experience",
        label="Максимальный стаж (дней)",
    )

    class Meta:
        model = Employee
        fields = ["skill", "min_experience_days", "max_experience_days"]

    def filter_min_experience(self, queryset, name, value):
        """Стаж ≥ value."""
        days = int(value)
        min_date = timezone.now().date() - timedelta(days=days)
        return queryset.filter(hire_date__lte=min_date)

    def filter_max_experience(self, queryset, name, value):
        """Стаж ≤ value."""
        days = int(value)
        max_date = timezone.now().date() - timedelta(days=days)
        return queryset.filter(hire_date__gte=max_date)
