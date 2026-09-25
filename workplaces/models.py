from django.core.validators import MinValueValidator
from django.db import models


class Workplace(models.Model):
    """Рабочее место (номер стола и дополнительная информация)."""

    desk_number = models.PositiveIntegerField(
        "Номер стола",
        unique=True,
        validators=[MinValueValidator(1)],
    )
    notes = models.TextField("Дополнительная информация", blank=True)

    class Meta:
        verbose_name = "Рабочее место"
        verbose_name_plural = "Рабочие места"
        ordering = ["desk_number"]

    def __str__(self):
        return f"Стол №{self.desk_number}"
