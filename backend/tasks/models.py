"""
Models for ToDo List application.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from .fields import ULIDField, generate_ulid


class User(AbstractUser):
    """
    Расширенная модель пользователя с ULID как первичным ключом.
    Хранит telegram_id для связи с Telegram ботом.
    """
    id = ULIDField(primary_key=True, default=generate_ulid)
    telegram_id = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True,
        verbose_name='Telegram ID'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Category(models.Model):
    """
    Модель категории (тега) для задач.
    """
    id = ULIDField(primary_key=True, default=generate_ulid)
    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    color = models.CharField(
        max_length=7,
        default='#3498db',
        verbose_name='Цвет',
        help_text='HEX код цвета, например #3498db'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name='Пользователь'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']
        unique_together = ['name', 'user']

    def __str__(self):
        return self.name


class Task(models.Model):
    """
    Модель задачи ToDo List.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'В ожидании'
        IN_PROGRESS = 'in_progress', 'В процессе'
        COMPLETED = 'completed', 'Завершена'

    id = ULIDField(primary_key=True, default=generate_ulid)
    title = models.CharField(
        max_length=255,
        verbose_name='Название'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Статус'
    )
    due_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата исполнения'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Пользователь'
    )
    categories = models.ManyToManyField(
        Category,
        related_name='tasks',
        blank=True,
        verbose_name='Категории'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    notification_sent = models.BooleanField(
        default=False,
        verbose_name='Уведомление отправлено'
    )

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
