from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from workplaces.models import Workplace


class Skill(models.Model):
    """Справочник навыков (бэкенд, фронтенд, тестирование и т.д.)."""

    name = models.CharField("Название навыка", max_length=100, unique=True)

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Employee(models.Model):
    """Сотрудник — расширение стандартной модели User."""

    class Gender(models.TextChoices):
        MALE = "M", "Мужской"
        FEMALE = "F", "Женский"
        OTHER = "O", "Другой"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="employee",
        verbose_name="Пользователь",
    )
    gender = models.CharField(
        "Пол",
        max_length=1,
        choices=Gender.choices,
        default=Gender.OTHER,
    )
    first_name = models.CharField("Имя", max_length=100)
    last_name = models.CharField("Фамилия", max_length=100)
    patronymic = models.CharField("Отчество", max_length=100, blank=True)
    description = models.TextField("Описание", blank=True)
    workplace = models.OneToOneField(
        Workplace,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee",
        verbose_name="Рабочее место",
    )
    skills = models.ManyToManyField(
        Skill,
        through="SkillLevel",
        related_name="employees",
        verbose_name="Навыки",
    )

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class SkillLevel(models.Model):
    """Уровень освоения навыка конкретным сотрудником (1–10)."""

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="skill_levels",
        verbose_name="Сотрудник",
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="skill_levels",
        verbose_name="Навык",
    )
    level = models.PositiveSmallIntegerField(
        "Уровень (1–10)",
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )

    class Meta:
        verbose_name = "Уровень навыка"
        verbose_name_plural = "Уровни навыков"
        unique_together = ("employee", "skill")
        ordering = ["employee", "-level"]

    def __str__(self):
        return f"{self.employee} — {self.skill}: {self.level}/10"
