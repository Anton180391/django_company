from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, TemplateView

from .models import Employee


class HomeView(TemplateView):
    """Главная страница — описание проекта + 4 последних сотрудника."""

    template_name = "employees/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Оптимизация запросов
        context["employees"] = (
            Employee.objects.select_related("workplace")
            .prefetch_related("skills", "images", "skill_levels__skill")
            .exclude(hire_date__isnull=True)
            .order_by("-hire_date")[:4]
        )
        # Общее количество сотрудников
        context["employees_count"] = Employee.objects.count()
        return context


class EmployeeListView(ListView):
    """Список всех сотрудников с пагинацией по 10."""

    model = Employee
    template_name = "employees/employee_list.html"
    context_object_name = "employees"
    paginate_by = 10

    def get_queryset(self):
        # Оптимизация запросов
        return (
            Employee.objects.select_related("workplace")
            .prefetch_related("skills", "images", "skill_levels__skill")
            .order_by("last_name", "first_name")
        )


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    """Подробная карточка сотрудника. Только для авторизованных."""

    model = Employee
    template_name = "employees/employee_detail.html"
    context_object_name = "employee"

    def get_queryset(self):
        # Оптимизация запросов
        return Employee.objects.select_related("workplace").prefetch_related(
            "skills", "images", "skill_levels__skill"
        )
