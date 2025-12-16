"""
API Views for ToDo List application.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import User, Category, Task
from .serializers import (
    UserSerializer, CategorySerializer, TaskSerializer,
    TaskListSerializer, UserRegistrationSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями."""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'])
    def register_telegram(self, request):
        """Регистрация пользователя через Telegram."""
        telegram_id = request.data.get('telegram_id')
        username = request.data.get('username')

        if not telegram_id:
            return Response(
                {'error': 'telegram_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем, существует ли пользователь с таким telegram_id
        user = User.objects.filter(telegram_id=telegram_id).first()
        if user:
            return Response(UserSerializer(user).data)

        # Создаем нового пользователя
        if not username:
            username = f'telegram_{telegram_id}'

        serializer = UserRegistrationSerializer(data={
            'username': username,
            'telegram_id': telegram_id
        })
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def by_telegram(self, request):
        """Получение пользователя по Telegram ID."""
        telegram_id = request.query_params.get('telegram_id')
        if not telegram_id:
            return Response(
                {'error': 'telegram_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(User, telegram_id=telegram_id)
        return Response(UserSerializer(user).data)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet для управления категориями."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        """Фильтрация категорий по пользователю."""
        queryset = Category.objects.all()
        user_id = self.request.query_params.get('user_id')
        telegram_id = self.request.query_params.get('telegram_id')

        if user_id:
            queryset = queryset.filter(user_id=user_id)
        elif telegram_id:
            queryset = queryset.filter(user__telegram_id=telegram_id)

        return queryset


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet для управления задачами."""
    queryset = Task.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return TaskSerializer

    def get_queryset(self):
        """Фильтрация задач по пользователю и статусу."""
        queryset = Task.objects.all().prefetch_related('categories')
        user_id = self.request.query_params.get('user_id')
        telegram_id = self.request.query_params.get('telegram_id')
        task_status = self.request.query_params.get('status')

        if user_id:
            queryset = queryset.filter(user_id=user_id)
        elif telegram_id:
            queryset = queryset.filter(user__telegram_id=telegram_id)

        if task_status:
            queryset = queryset.filter(status=task_status)

        return queryset

    @action(detail=False, methods=['get'])
    def by_telegram(self, request):
        """Получение задач пользователя по Telegram ID."""
        telegram_id = request.query_params.get('telegram_id')
        if not telegram_id:
            return Response(
                {'error': 'telegram_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        tasks = Task.objects.filter(
            user__telegram_id=telegram_id
        ).prefetch_related('categories').order_by('-created_at')

        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def create_for_telegram(self, request):
        """Создание задачи для пользователя по Telegram ID."""
        telegram_id = request.data.get('telegram_id')
        if not telegram_id:
            return Response(
                {'error': 'telegram_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(User, telegram_id=telegram_id)

        data = request.data.copy()
        data['user'] = user.id

        serializer = TaskSerializer(data=data)
        if serializer.is_valid():
            task = serializer.save()
            return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def health_check(request):
    """Проверка работоспособности API."""
    return Response({'status': 'ok'})
