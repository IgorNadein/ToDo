"""
Tests for Django models: User, Category, Task and ULID field.
"""

import pytest
from django.utils import timezone
from datetime import timedelta

from tasks.models import User, Category, Task
from tasks.fields import generate_ulid, ULIDField


class TestULIDField:
    """Tests for ULID field implementation."""

    def test_generate_ulid_returns_string(self):
        """Test that generate_ulid returns a string."""
        ulid = generate_ulid()
        assert isinstance(ulid, str)

    def test_generate_ulid_length(self):
        """Test that ULID has correct length (26 characters)."""
        ulid = generate_ulid()
        assert len(ulid) == 26

    def test_generate_ulid_unique(self):
        """Test that generated ULIDs are unique."""
        ulids = [generate_ulid() for _ in range(100)]
        assert len(set(ulids)) == 100

    def test_ulid_field_default_max_length(self):
        """Test ULIDField default max_length."""
        field = ULIDField()
        assert field.max_length == 26

    def test_ulid_field_not_editable(self):
        """Test ULIDField is not editable by default."""
        field = ULIDField()
        assert field.editable is False

    def test_ulid_field_deconstruct(self):
        """Test ULIDField deconstruct method."""
        field = ULIDField()
        name, path, args, kwargs = field.deconstruct()
        assert 'max_length' not in kwargs
        assert 'default' not in kwargs
        assert 'editable' not in kwargs


class TestUserModel:
    """Tests for User model."""

    def test_user_creation(self, db):
        """Test creating a user."""
        user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='password123'
        )
        assert user.pk is not None
        assert len(user.pk) == 26  # ULID length
        assert user.username == 'newuser'

    def test_user_with_telegram_id(self, db):
        """Test creating user with telegram_id."""
        user = User.objects.create_user(
            username='telegramuser',
            telegram_id=123456789
        )
        assert user.telegram_id == 123456789

    def test_user_telegram_id_unique(self, user, db):
        """Test that telegram_id is unique."""
        with pytest.raises(Exception):
            User.objects.create_user(
                username='duplicate_telegram',
                telegram_id=user.telegram_id
            )

    def test_user_str_representation(self, user):
        """Test user string representation."""
        assert str(user) == user.username

    def test_user_ulid_as_primary_key(self, user):
        """Test that user uses ULID as primary key."""
        assert isinstance(user.pk, str)
        assert len(user.pk) == 26


class TestCategoryModel:
    """Tests for Category model."""

    def test_category_creation(self, db, user):
        """Test creating a category."""
        category = Category.objects.create(
            name='Work',
            color='#3498db',
            user=user
        )
        assert category.pk is not None
        assert len(category.pk) == 26
        assert category.name == 'Work'

    def test_category_default_color(self, db, user):
        """Test category default color."""
        category = Category.objects.create(
            name='Default Color',
            user=user
        )
        assert category.color == '#3498db'

    def test_category_str_representation(self, category):
        """Test category string representation."""
        assert str(category) == category.name

    def test_category_user_relationship(self, category, user):
        """Test category belongs to user."""
        assert category.user == user
        assert category in user.categories.all()

    def test_category_unique_name_per_user(self, category, user, db):
        """Test that category name is unique per user."""
        with pytest.raises(Exception):
            Category.objects.create(
                name=category.name,
                user=user
            )

    def test_category_same_name_different_users(self, user, another_user, db):
        """Test that same category name can exist for different users."""
        Category.objects.create(name='Shared Name', user=user)
        cat2 = Category.objects.create(name='Shared Name', user=another_user)
        assert cat2.pk is not None

    def test_category_created_at_auto(self, category):
        """Test that created_at is set automatically."""
        assert category.created_at is not None

    def test_category_ordering(self, db, user):
        """Test category ordering by name."""
        Category.objects.create(name='Zebra', user=user)
        Category.objects.create(name='Apple', user=user)
        categories = list(Category.objects.filter(user=user))
        assert categories[0].name == 'Apple'


class TestTaskModel:
    """Tests for Task model."""

    def test_task_creation(self, db, user):
        """Test creating a task."""
        task = Task.objects.create(
            title='New Task',
            description='Task description',
            user=user
        )
        assert task.pk is not None
        assert len(task.pk) == 26
        assert task.title == 'New Task'

    def test_task_default_status(self, db, user):
        """Test task default status is pending."""
        task = Task.objects.create(
            title='Default Status Task',
            user=user
        )
        assert task.status == 'pending'

    def test_task_status_choices(self, db, user):
        """Test task status choices."""
        for status in ['pending', 'in_progress', 'completed']:
            task = Task.objects.create(
                title=f'Task {status}',
                status=status,
                user=user
            )
            assert task.status == status

    def test_task_str_representation(self, task):
        """Test task string representation."""
        assert str(task) == task.title

    def test_task_with_due_date(self, db, user):
        """Test task with due date."""
        due = timezone.now() + timedelta(days=7)
        task = Task.objects.create(
            title='Task with due date',
            due_date=due,
            user=user
        )
        assert task.due_date is not None

    def test_task_categories_many_to_many(self, task, category, another_category):
        """Test task can have multiple categories."""
        task.categories.add(another_category)
        assert task.categories.count() == 2

    def test_task_notification_sent_default(self, db, user):
        """Test notification_sent defaults to False."""
        task = Task.objects.create(
            title='Notification Test',
            user=user
        )
        assert task.notification_sent is False

    def test_task_created_at_auto(self, task):
        """Test created_at is set automatically."""
        assert task.created_at is not None

    def test_task_updated_at_auto(self, task, db):
        """Test updated_at is updated on save."""
        old_updated = task.updated_at
        task.title = 'Updated Title'
        task.save()
        task.refresh_from_db()
        assert task.updated_at > old_updated

    def test_task_ordering(self, multiple_tasks):
        """Test tasks are ordered by created_at descending."""
        tasks = list(Task.objects.all())
        for i in range(len(tasks) - 1):
            assert tasks[i].created_at >= tasks[i + 1].created_at

    def test_task_cascade_delete_user(self, task, user, db):
        """Test tasks are deleted when user is deleted."""
        task_id = task.pk
        user.delete()
        assert not Task.objects.filter(pk=task_id).exists()

    def test_category_cascade_delete_user(self, category, user, db):
        """Test categories are deleted when user is deleted."""
        category_id = category.pk
        user.delete()
        assert not Category.objects.filter(pk=category_id).exists()
