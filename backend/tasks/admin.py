"""
Admin configuration for ToDo List application.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Category, Task


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Административный интерфейс для модели User."""
    list_display = ['username', 'email', 'telegram_id', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email', 'telegram_id']
    ordering = ['-date_joined']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Telegram', {'fields': ('telegram_id',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Telegram', {'fields': ('telegram_id',)}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели Category."""
    list_display = ['name', 'user', 'color', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['name', 'user__username']
    ordering = ['name']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели Task."""
    list_display = ['title', 'user', 'status', 'due_date', 'notification_sent', 'created_at']
    list_filter = ['status', 'notification_sent', 'created_at', 'due_date']
    search_fields = ['title', 'description', 'user__username']
    filter_horizontal = ['categories']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'user')
        }),
        ('Статус и сроки', {
            'fields': ('status', 'due_date', 'notification_sent')
        }),
        ('Категории', {
            'fields': ('categories',)
        }),
    )
