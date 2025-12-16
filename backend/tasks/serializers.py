"""
Serializers for ToDo List API.
"""

from rest_framework import serializers
from .models import User, Category, Task


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'telegram_id', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        fields = ['id', 'name', 'color', 'user', 'created_at']
        read_only_fields = ['id', 'created_at']


class CategoryListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка категорий (без пользователя)."""

    class Meta:
        model = Category
        fields = ['id', 'name', 'color']


class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Task."""
    categories = CategoryListSerializer(many=True, read_only=True)
    category_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status',
            'due_date', 'user', 'categories', 'category_ids',
            'created_at', 'updated_at', 'notification_sent'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'notification_sent']

    def create(self, validated_data):
        category_ids = validated_data.pop('category_ids', [])
        task = Task.objects.create(**validated_data)
        if category_ids:
            categories = Category.objects.filter(id__in=category_ids, user=task.user)
            task.categories.set(categories)
        return task

    def update(self, instance, validated_data):
        category_ids = validated_data.pop('category_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if category_ids is not None:
            categories = Category.objects.filter(id__in=category_ids, user=instance.user)
            instance.categories.set(categories)
        return instance


class TaskListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка задач с категориями."""
    categories = CategoryListSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status',
            'due_date', 'categories', 'created_at'
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя через Telegram."""

    class Meta:
        model = User
        fields = ['id', 'username', 'telegram_id']
        read_only_fields = ['id']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            telegram_id=validated_data.get('telegram_id')
        )
        return user
