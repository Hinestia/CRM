from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    ADMIN = "admin", "Администратор"
    ACCOUNTANT = "accountant", "Бухгалтер"
    PASSPORT_OFFICER = "passport_officer", "Паспортист"
    ENGINEER = "engineer", "Инженер"
    READONLY = "readonly", "Только просмотр"


class User(AbstractUser):
    """Кастомная модель пользователя системы (сотрудник).

    role используется для быстрой фильтрации/отображения в интерфейсе;
    фактические права доступа выдаются через стандартные группы и права
    Django (см. миграцию данных 0002_default_groups), привязанные к роли.
    """

    role = models.CharField(
        "Роль",
        max_length=20,
        choices=Role.choices,
        default=Role.READONLY,
    )
    phone = models.CharField("Телефон", max_length=20, blank=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_accountant(self):
        return self.role == Role.ACCOUNTANT or self.is_superuser

    @property
    def is_passport_officer(self):
        return self.role == Role.PASSPORT_OFFICER or self.is_superuser

    @property
    def is_engineer(self):
        return self.role == Role.ENGINEER or self.is_superuser
