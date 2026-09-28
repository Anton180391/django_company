from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, TemplateView

from .models import Employee


class HomeView(TemplateView):
    """Главная страница — описание проекта + карточки сотрудников."""

    template_name = "employees/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["employees"] = Employee.objects.prefetch_related("skills", "images")[:6]
        return context


class EmployeeListView(ListView):
    """Список всех сотрудников."""

    model = Employee
    template_name = "employees/employee_list.html"
    context_object_name = "employees"
    paginate_by = 12


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    """Подробная карточка сотрудника. Только для авторизованных."""

    model = Employee
    template_name = "employees/employee_detail.html"
    context_object_name = "employee"

    def get_queryset(self):
        return Employee.objects.prefetch_related(
            "skills", "images", "skill_levels__skill"
        )
