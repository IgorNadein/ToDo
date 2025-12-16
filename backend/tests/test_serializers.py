"""
Tests for serializers: UserSerializer, CategorySerializer, TaskSerializer.
"""

from django.utils import timezone
from datetime import timedelta

from tasks.serializers import (
    UserSerializer,
    CategorySerializer,
    CategoryListSerializer,
    TaskSerializer,
    TaskListSerializer,
    UserRegistrationSerializer,
)


class TestUserSerializer:
    """Tests for UserSerializer."""

    def test_serialize_user(self, user):
        """Test serializing a user."""
        serializer = UserSerializer(user)
        data = serializer.data

        assert data['id'] == user.id
        assert data['username'] == user.username
        assert data['email'] == user.email
        assert data['telegram_id'] == user.telegram_id
        assert 'date_joined' in data

    def test_user_id_is_read_only(self, user):
        """Test that id is read-only."""
        serializer = UserSerializer(user, data={'id': 'new-id'}, partial=True)
        assert serializer.is_valid()
        # id should not change
        assert 'id' not in serializer.validated_data


class TestUserRegistrationSerializer:
    """Tests for UserRegistrationSerializer."""

    def test_create_user(self, db):
        """Test creating user through serializer."""
        data = {
            'username': 'newuser',
            'telegram_id': 111222333
        }
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()

        assert user.pk is not None
        assert user.username == 'newuser'
        assert user.telegram_id == 111222333

    def test_username_required(self, db):
        """Test username is required."""
        data = {'telegram_id': 111222333}
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'username' in serializer.errors


class TestCategorySerializer:
    """Tests for CategorySerializer."""

    def test_serialize_category(self, category):
        """Test serializing a category."""
        serializer = CategorySerializer(category)
        data = serializer.data

        assert data['id'] == category.id
        assert data['name'] == category.name
        assert data['color'] == category.color
        assert data['user'] == category.user.id
        assert 'created_at' in data

    def test_create_category(self, db, user):
        """Test creating category through serializer."""
        data = {
            'name': 'New Category',
            'color': '#abcdef',
            'user': user.id
        }
        serializer = CategorySerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        category = serializer.save()

        assert category.name == 'New Category'
        assert category.color == '#abcdef'

    def test_category_name_required(self, db, user):
        """Test name is required."""
        data = {'color': '#ffffff', 'user': user.id}
        serializer = CategorySerializer(data=data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors


class TestCategoryListSerializer:
    """Tests for CategoryListSerializer."""

    def test_serialize_category_list(self, category):
        """Test serializing category for list view."""
        serializer = CategoryListSerializer(category)
        data = serializer.data

        assert data['id'] == category.id
        assert data['name'] == category.name
        assert data['color'] == category.color
        assert 'user' not in data
        assert 'created_at' not in data


class TestTaskSerializer:
    """Tests for TaskSerializer."""

    def test_serialize_task(self, task):
        """Test serializing a task."""
        serializer = TaskSerializer(task)
        data = serializer.data

        assert data['id'] == task.id
        assert data['title'] == task.title
        assert data['description'] == task.description
        assert data['status'] == task.status
        assert data['user'] == task.user.id
        assert 'categories' in data
        assert 'created_at' in data
        assert 'updated_at' in data

    def test_create_task(self, db, user):
        """Test creating task through serializer."""
        data = {
            'title': 'New Task',
            'description': 'Description',
            'status': 'pending',
            'user': user.id
        }
        serializer = TaskSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        task = serializer.save()

        assert task.title == 'New Task'
        assert task.user == user

    def test_create_task_with_categories(self, db, user, category, another_category):
        """Test creating task with category_ids."""
        data = {
            'title': 'Task with categories',
            'user': user.id,
            'category_ids': [category.id, another_category.id]
        }
        serializer = TaskSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        task = serializer.save()

        assert task.categories.count() == 2

    def test_update_task(self, task, db):
        """Test updating task through serializer."""
        data = {'title': 'Updated Title'}
        serializer = TaskSerializer(task, data=data, partial=True)
        assert serializer.is_valid()
        updated = serializer.save()

        assert updated.title == 'Updated Title'

    def test_update_task_categories(self, task, another_category, db):
        """Test updating task categories."""
        data = {'category_ids': [another_category.id]}
        serializer = TaskSerializer(task, data=data, partial=True)
        assert serializer.is_valid()
        updated = serializer.save()

        assert updated.categories.count() == 1
        assert another_category in updated.categories.all()

    def test_task_title_required(self, db, user):
        """Test title is required."""
        data = {'description': 'No title', 'user': user.id}
        serializer = TaskSerializer(data=data)
        assert not serializer.is_valid()
        assert 'title' in serializer.errors

    def test_task_with_due_date(self, db, user):
        """Test creating task with due_date."""
        due = timezone.now() + timedelta(days=3)
        data = {
            'title': 'Task with due date',
            'user': user.id,
            'due_date': due.isoformat()
        }
        serializer = TaskSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        task = serializer.save()

        assert task.due_date is not None


class TestTaskListSerializer:
    """Tests for TaskListSerializer."""

    def test_serialize_task_list(self, task):
        """Test serializing task for list view."""
        serializer = TaskListSerializer(task)
        data = serializer.data

        assert data['id'] == task.id
        assert data['title'] == task.title
        assert data['status'] == task.status
        assert 'categories' in data
        assert 'created_at' in data
        # Should not include update fields
        assert 'updated_at' not in data
        assert 'notification_sent' not in data

    def test_serialize_multiple_tasks(self, multiple_tasks):
        """Test serializing multiple tasks."""
        serializer = TaskListSerializer(multiple_tasks, many=True)
        data = serializer.data

        assert len(data) == 5
        for item in data:
            assert 'id' in item
            assert 'title' in item
            assert 'categories' in item
