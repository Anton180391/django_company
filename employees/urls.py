from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .api_views import EmployeeViewSet
from .views import EmployeeDetailView, EmployeeListView, HomeView

app_name = "employees"

# Router для API
router = DefaultRouter()
router.register(r"employees", EmployeeViewSet, basename="employee")

urlpatterns = [
    # HTML-страницы
    path("", HomeView.as_view(), name="home"),
    path("employees/", EmployeeListView.as_view(), name="employee_list"),
    path(
        "employees/<int:pk>/",
        EmployeeDetailView.as_view(),
        name="employee_detail",
    ),
    # API
    path("api/", include(router.urls)),
    path(
        "api/token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "api/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
]
