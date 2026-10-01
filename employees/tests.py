from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from workplaces.models import Workplace

from .models import Employee, Skill, SkillLevel


class BaseTestCase(TestCase):
    """Базовая настройка данных для всех тестов."""

    def setUp(self):
        """Создаём тестовые данные перед каждым тестом."""
        # Пользователи
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", password="otherpass123"
        )

        # Навыки
        self.skill_backend = Skill.objects.create(name="Бэкенд")
        self.skill_frontend = Skill.objects.create(name="Фронтенд")
        self.skill_qa = Skill.objects.create(name="Тестирование")

        # Рабочие места
        self.workplace_1 = Workplace.objects.create(desk_number=1)
        self.workplace_2 = Workplace.objects.create(desk_number=2)
        self.workplace_3 = Workplace.objects.create(desk_number=3)
        self.workplace_4 = Workplace.objects.create(desk_number=4)

        # Сотрудник-разработчик (без стола — чтобы не было конфликтов)
        self.employee_dev = Employee.objects.create(
            user=self.user,
            gender="M",
            first_name="Иван",
            last_name="Петров",
            hire_date=date.today() - timedelta(days=30),
            workplace=self.workplace_1,
        )
        SkillLevel.objects.create(
            employee=self.employee_dev, skill=self.skill_backend, level=8
        )


# ═══════════════════════════════════════════════════════════
# K1: ГЛАВНАЯ СТРАНИЦА
# ═══════════════════════════════════════════════════════════


class HomeViewTests(BaseTestCase):
    """Тесты главной страницы."""

    def test_home_url_accessible(self):
        """Главная доступна без авторизации."""
        response = self.client.get(reverse("employees:home"))
        self.assertEqual(response.status_code, 200)

    def test_home_uses_correct_template(self):
        """Используется шаблон home.html."""
        response = self.client.get(reverse("employees:home"))
        self.assertTemplateUsed(response, "employees/home.html")

    def test_home_context_has_employees_count(self):
        """В контексте есть employees_count."""
        response = self.client.get(reverse("employees:home"))
        self.assertIn("employees_count", response.context)
        self.assertEqual(response.context["employees_count"], 1)

    def test_home_context_has_employees(self):
        """В контексте есть employees (4 последних)."""
        response = self.client.get(reverse("employees:home"))
        self.assertIn("employees", response.context)
        self.assertEqual(len(response.context["employees"]), 1)


# ═══════════════════════════════════════════════════════════
# K2: СПИСОК СОТРУДНИКОВ
# ═══════════════════════════════════════════════════════════


class EmployeeListViewTests(BaseTestCase):
    """Тесты списка сотрудников."""

    def test_list_url_accessible(self):
        """Список доступен без авторизации."""
        response = self.client.get(reverse("employees:employee_list"))
        self.assertEqual(response.status_code, 200)

    def test_list_uses_correct_template(self):
        """Используется шаблон employee_list.html."""
        response = self.client.get(reverse("employees:employee_list"))
        self.assertTemplateUsed(response, "employees/employee_list.html")

    def test_list_context_has_employees(self):
        """В контексте есть employees."""
        response = self.client.get(reverse("employees:employee_list"))
        self.assertIn("employees", response.context)
        self.assertEqual(len(response.context["employees"]), 1)

    def test_list_pagination_10_per_page(self):
        """Пагинация по 10 на странице."""
        # Создаём 15 сотрудников
        for i in range(15):
            user = User.objects.create_user(username=f"user{i}")
            Employee.objects.create(
                user=user,
                first_name=f"Имя{i}",
                last_name=f"Фамилия{i}",
                hire_date=date.today(),
            )
        response = self.client.get(reverse("employees:employee_list"))
        self.assertEqual(len(response.context["employees"]), 10)
        self.assertTrue(response.context["is_paginated"])


# ═══════════════════════════════════════════════════════════
# K3, K4: ДЕТАЛЬНАЯ СТРАНИЦА
# ═══════════════════════════════════════════════════════════


class EmployeeDetailViewTests(BaseTestCase):
    """Тесты прав доступа к детальной странице."""

    def test_detail_anonymous_redirected(self):
        """Гость перенаправляется на логин."""
        url = reverse("employees:employee_detail", args=[self.employee_dev.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_detail_authorized_accessible(self):
        """Авторизованный видит страницу."""
        self.client.login(username="testuser", password="testpass123")
        url = reverse("employees:employee_detail", args=[self.employee_dev.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_detail_uses_correct_template(self):
        """Используется шаблон employee_detail.html."""
        self.client.login(username="testuser", password="testpass123")
        url = reverse("employees:employee_detail", args=[self.employee_dev.pk])
        response = self.client.get(url)
        self.assertTemplateUsed(response, "employees/employee_detail.html")

    def test_detail_context_has_employee(self):
        """В контексте есть employee."""
        self.client.login(username="testuser", password="testpass123")
        url = reverse("employees:employee_detail", args=[self.employee_dev.pk])
        response = self.client.get(url)
        self.assertIn("employee", response.context)
        self.assertEqual(response.context["employee"], self.employee_dev)

    def test_detail_404_for_unknown_employee(self):
        """Несуществующий сотрудник → 404."""
        self.client.login(username="testuser", password="testpass123")
        url = reverse("employees:employee_detail", args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


# ═══════════════════════════════════════════════════════════
# K5: ВАЛИДАТОР
# ═══════════════════════════════════════════════════════════


class EmployeeValidatorTests(BaseTestCase):
    """Тесты валидатора соседних столов."""

    def test_qa_next_to_dev_raises_error(self):
        """Тестировщик не может сидеть рядом с разработчиком."""
        # Разработчик уже сидит за столом №1 (в setUp)
        # Создаём тестировщика за столом №2
        qa_user = User.objects.create_user(username="qauser")
        qa_employee = Employee(
            user=qa_user,
            first_name="Ольга",
            last_name="Тестировщик",
            hire_date=date.today(),
            workplace=self.workplace_2,
        )
        qa_employee.save()
        SkillLevel.objects.create(employee=qa_employee, skill=self.skill_qa, level=9)

        # Пересохраняем, чтобы вызвать clean() с уже установленными навыками
        qa_employee.refresh_from_db()

        with self.assertRaises(ValidationError):
            qa_employee.clean()

    def test_dev_next_to_qa_raises_error(self):
        """Разработчик не может сидеть рядом с тестировщиком."""
        # Создаём тестировщика за столом №2
        qa_user = User.objects.create_user(username="qauser")
        qa_employee = Employee.objects.create(
            user=qa_user,
            first_name="Ольга",
            last_name="Тестировщик",
            hire_date=date.today(),
            workplace=self.workplace_2,
        )
        SkillLevel.objects.create(employee=qa_employee, skill=self.skill_qa, level=9)

        # Создаём разработчика за столом №3 (соседний со столом №2)
        dev_user = User.objects.create_user(username="devuser")
        dev_employee = Employee(
            user=dev_user,
            first_name="Сергей",
            last_name="Разработчик",
            hire_date=date.today(),
            workplace=self.workplace_3,
        )
        dev_employee.save()
        SkillLevel.objects.create(
            employee=dev_employee, skill=self.skill_backend, level=8
        )

        dev_employee.refresh_from_db()

        with self.assertRaises(ValidationError):
            dev_employee.clean()

    def test_dev_next_to_dev_no_error(self):
        """Два разработчика могут сидеть рядом."""
        # Разработчик уже за столом №1
        # Создаём второго разработчика за столом №2
        dev2_user = User.objects.create_user(username="dev2")
        dev2_employee = Employee(
            user=dev2_user,
            first_name="Пётр",
            last_name="Разработчик",
            hire_date=date.today(),
            workplace=self.workplace_2,
        )
        dev2_employee.save()
        SkillLevel.objects.create(
            employee=dev2_employee, skill=self.skill_backend, level=7
        )

        dev2_employee.refresh_from_db()

        # Не должно быть ошибки
        try:
            dev2_employee.clean()
        except ValidationError:
            self.fail("Валидатор ошибочно сработал для двух разработчиков")
