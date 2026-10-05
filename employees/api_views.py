from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .filters import EmployeeFilter
from .models import Employee
from .permissions import CanManageWorkplace, IsAdministrator
from .serializers import (
    EmployeeCreateUpdateSerializer,
    EmployeeDetailSerializer,
    EmployeeListSerializer,
    EmployeeWorkplaceSerializer,
)


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для сотрудников.

    list: список (пагинация 10, фильтрация)
    retrieve: детальная информация
    create: создание (только админ)
    update: обновление (только админ)
    destroy: удаление (только админ)
    set_workplace: перемещение за стол (смотритель/админ)
    """

    queryset = Employee.objects.select_related("workplace").prefetch_related(
        "skill_levels__skill", "images"
    )
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = EmployeeFilter
    search_fields = ["first_name", "last_name", "patronymic"]
    ordering_fields = ["hire_date", "last_name"]

    def get_serializer_class(self):
        if self.action == "list":
            return EmployeeListSerializer
        if self.action in ("create", "update", "partial_update"):
            return EmployeeCreateUpdateSerializer
        if self.action == "set_workplace":
            return EmployeeWorkplaceSerializer
        return EmployeeDetailSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAdministrator()]
        if self.action == "set_workplace":
            return [CanManageWorkplace()]
        return [IsAuthenticatedOrReadOnly()]

    @action(
        detail=True,
        methods=["patch"],
        url_path="set-workplace",
        permission_classes=[CanManageWorkplace],
    )
    def set_workplace(self, request, pk=None):
        """Переместить сотрудника за другой стол (смотритель/админ)."""
        employee = self.get_object()
        serializer = EmployeeWorkplaceSerializer(
            employee, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
