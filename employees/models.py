from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
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
    hire_date = models.DateField(
        "Дата приёма на работу",
        null=True,
        blank=True,
    )
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

    @property
    def full_name(self):
        """Полное имя сотрудника."""
        parts = [self.last_name, self.first_name, self.patronymic]
        return " ".join(p for p in parts if p)

    @property
    def experience_days(self):
        """Стаж работы в компании (в днях)."""
        if not self.hire_date:
            return 0
        from django.utils import timezone

        return (timezone.now().date() - self.hire_date).days

    @property
    def main_image(self):
        """Первое изображение из галереи."""
        return self.images.first()

    @property
    def other_images(self):
        """Все изображения, кроме первого."""
        return self.images.all()[1:]

    def clean(self):
        """Валидация: тестировщики и разработчики не за соседними столами."""
        super().clean()

        if not self.workplace or not self.pk:
            return

        current_category = self._get_category()
        if not current_category:
            return

        neighbor_desks = [
            self.workplace.desk_number - 1,
            self.workplace.desk_number + 1,
        ]

        neighbors = Employee.objects.filter(
            workplace__desk_number__in=neighbor_desks
        ).exclude(pk=self.pk)

        for neighbor in neighbors:
            neighbor_category = neighbor._get_category()
            if current_category == "dev" and neighbor_category == "qa":
                raise ValidationError(
                    f"Разработчик не может сидеть рядом с тестировщиком! "
                    f"За столом №{neighbor.workplace.desk_number} работает тестировщик."
                )
            if current_category == "qa" and neighbor_category == "dev":
                raise ValidationError(
                    f"Тестировщик не может сидеть рядом с разработчиком! "
                    f"За столом №{neighbor.workplace.desk_number} работает разработчик."
                )

    def _get_category(self):
        """Возвращает 'qa', 'dev' или None — в зависимости от навыков."""
        if not self.pk:
            return None

        try:
            skill_names = [s.name.lower() for s in self.skills.all()]
        except ValueError:
            return None

        has_qa = any("тест" in name for name in skill_names)
        has_dev = any(
            "бэкенд" in name or "фронтенд" in name or "разработ" in name
            for name in skill_names
        )

        if has_qa and not has_dev:
            return "qa"
        if has_dev and not has_qa:
            return "dev"
        return None


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


class EmployeeImage(models.Model):
    """Изображение в галерее сотрудника."""

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Сотрудник",
    )
    image = models.ImageField("Изображение", upload_to="employees/%Y/%m/%d/")
    order = models.PositiveIntegerField("Порядковый номер", default=0)

    class Meta:
        verbose_name = "Изображение сотрудника"
        verbose_name_plural = "Изображения сотрудников"
        ordering = ["order", "id"]

    def __str__(self):
        return f"Изображение #{self.order} — {self.employee}"

    def delete(self, *args, **kwargs):
        """Удаляем файл с диска перед удалением записи."""
        self.image.delete(save=False)
        super().delete(*args, **kwargs)
