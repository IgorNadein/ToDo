"""
Pytest configuration and fixtures for Django backend tests.
"""

import pytest
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient

from tasks.models import User, Category, Task


@pytest.fixture
def api_client():
    """Returns DRF API test client."""
    return APIClient()


@pytest.fixture
def user(db):
    """Creates a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        telegram_id=123456789
    )


@pytest.fixture
def user_without_telegram(db):
    """Creates a test user without telegram_id."""
    return User.objects.create_user(
        username='user_no_telegram',
        email='notelegram@example.com',
        password='testpass123',
        telegram_id=None
    )


@pytest.fixture
def another_user(db):
    """Creates another test user."""
    return User.objects.create_user(
        username='anotheruser',
        email='another@example.com',
        password='testpass123',
        telegram_id=987654321
    )


@pytest.fixture
def category(db, user):
    """Creates a test category."""
    return Category.objects.create(
        name='Test Category',
        color='#ff5733',
        user=user
    )


@pytest.fixture
def another_category(db, user):
    """Creates another test category."""
    return Category.objects.create(
        name='Another Category',
        color='#33ff57',
        user=user
    )


@pytest.fixture
def task(db, user, category):
    """Creates a test task with category."""
    task = Task.objects.create(
        title='Test Task',
        description='Test description',
        status='pending',
        due_date=timezone.now() + timedelta(days=1),
        user=user
    )
    task.categories.add(category)
    return task


@pytest.fixture
def task_without_due_date(db, user):
    """Creates a test task without due date."""
    return Task.objects.create(
        title='Task without due date',
        description='No due date',
        status='pending',
        user=user
    )


@pytest.fixture
def completed_task(db, user):
    """Creates a completed test task."""
    return Task.objects.create(
        title='Completed Task',
        description='This task is done',
        status='completed',
        user=user
    )


@pytest.fixture
def overdue_task(db, user):
    """Creates an overdue task for notification testing."""
    return Task.objects.create(
        title='Overdue Task',
        description='This task is overdue',
        status='pending',
        due_date=timezone.now() - timedelta(hours=1),
        user=user,
        notification_sent=False
    )


@pytest.fixture
def task_with_notification_sent(db, user):
    """Creates a task with notification already sent."""
    return Task.objects.create(
        title='Notified Task',
        description='Notification was sent',
        status='pending',
        due_date=timezone.now() - timedelta(hours=1),
        user=user,
        notification_sent=True
    )


@pytest.fixture
def multiple_tasks(db, user, category):
    """Creates multiple tasks for list testing."""
    tasks = []
    for i in range(5):
        task = Task.objects.create(
            title=f'Task {i}',
            description=f'Description {i}',
            status='pending' if i % 2 == 0 else 'in_progress',
            due_date=timezone.now() + timedelta(days=i),
            user=user
        )
        if i % 2 == 0:
            task.categories.add(category)
        tasks.append(task)
    return tasks
