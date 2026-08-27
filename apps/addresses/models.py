from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class StreetType(models.TextChoices):
    STREET = "street", "улица"
    AVENUE = "avenue", "проспект"
    LANE = "lane", "переулок"
    BOULEVARD = "boulevard", "бульвар"
    SQUARE = "square", "площадь"
    HIGHWAY = "highway", "шоссе"
    MICRODISTRICT = "microdistrict", "микрорайон"


class Street(models.Model):
    """Элемент адресного фонда: улица/проспект/переулок и т.п."""

    type = models.CharField("Тип", max_length=20, choices=StreetType.choices)
    name = models.CharField("Наименование", max_length=150)

    class Meta:
        verbose_name = "Улица"
        verbose_name_plural = "Улицы"
        unique_together = ("type", "name")
        ordering = ("name",)

    def __str__(self):
        return f"{self.get_type_display()} {self.name}"


class House(models.Model):
    """Дом на улице (с учётом корпуса/строения)."""

    street = models.ForeignKey(
        Street, on_delete=models.PROTECT, related_name="houses", verbose_name="Улица"
    )
    number = models.CharField("Номер дома", max_length=10)
    building = models.CharField(
        "Корпус/строение", max_length=10, blank=True, help_text="Например: корпус 2, строение 1"
    )

    class Meta:
        verbose_name = "Дом"
        verbose_name_plural = "Дома"
        unique_together = ("street", "number", "building")
        ordering = ("street", "number")

    def __str__(self):
        house_part = f"д.{self.number}"
        if self.building:
            house_part += f" к.{self.building}"
        return f"{self.street}, {house_part}"


class UnitType(models.TextChoices):
    RESIDENTIAL = "residential", "жилое помещение"
    NON_RESIDENTIAL = "non_residential", "нежилое помещение"


class Unit(models.Model):
    """Помещение (квартира/офис) — характеристики используются в начислениях."""

    house = models.ForeignKey(
        House, on_delete=models.PROTECT, related_name="units", verbose_name="Дом"
    )
    number = models.CharField("Номер помещения", max_length=10)
    type = models.CharField(
        "Тип помещения", max_length=20, choices=UnitType.choices, default=UnitType.RESIDENTIAL
    )

    area_living = models.DecimalField(
        "S жилая, м²", max_digits=8, decimal_places=2,
        default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))],
    )
    area_non_living = models.DecimalField(
        "S нежилая, м²", max_digits=8, decimal_places=2,
        default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))],
    )
    area_total = models.DecimalField(
        "S общая, м²", max_digits=8, decimal_places=2,
        default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))],
    )

    class Meta:
        verbose_name = "Помещение"
        verbose_name_plural = "Помещения"
        unique_together = ("house", "number")
        ordering = ("house", "number")

    def __str__(self):
        return f"{self.house}, кв. {self.number}"

    def save(self, *args, **kwargs):
        self.area_total = self.area_living + self.area_non_living
        super().save(*args, **kwargs)
