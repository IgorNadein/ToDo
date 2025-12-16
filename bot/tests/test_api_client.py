"""
Tests for API client module.
"""

import pytest
import re
from aioresponses import aioresponses

from api_client import APIClient, api_client


class TestAPIClient:
    """Tests for APIClient class."""

    @pytest.fixture
    def client(self):
        """Create API client instance."""
        return APIClient()

    @pytest.mark.asyncio
    async def test_register_user_success(
        self, client, sample_user_response
    ):
        """Test successful user registration."""
        with aioresponses() as m:
            m.post(
                f'{client.base_url}/users/register_telegram/',
                payload=sample_user_response
            )

            result = await client.register_user(123456789, 'testuser')

            assert result is not None
            assert result['telegram_id'] == 123456789

    @pytest.mark.asyncio
    async def test_register_user_failure(self, client):
        """Test user registration failure."""
        with aioresponses() as m:
            m.post(
                f'{client.base_url}/users/register_telegram/',
                status=500
            )

            result = await client.register_user(123456789, 'testuser')

            assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_telegram_success(
        self, client, sample_user_response
    ):
        """Test getting user by telegram_id."""
        with aioresponses() as m:
            pattern = re.compile(r'.*/users/by_telegram/.*')
            m.get(pattern, payload=sample_user_response)

            result = await client.get_user_by_telegram(123456789)

            assert result is not None
            assert result['username'] == 'testuser'

    @pytest.mark.asyncio
    async def test_get_user_by_telegram_not_found(self, client):
        """Test getting non-existent user."""
        with aioresponses() as m:
            pattern = re.compile(r'.*/users/by_telegram/.*')
            m.get(pattern, status=404)

            result = await client.get_user_by_telegram(999999999)

            assert result is None

    @pytest.mark.asyncio
    async def test_get_tasks_success(
        self, client, sample_tasks_response
    ):
        """Test getting tasks list."""
        with aioresponses() as m:
            pattern = re.compile(r'.*/tasks/by_telegram/.*')
            m.get(pattern, payload=sample_tasks_response)

            result = await client.get_tasks(123456789)

            assert result is not None
            assert len(result) == 2
            assert result[0]['title'] == 'Test Task 1'

    @pytest.mark.asyncio
    async def test_get_tasks_empty(self, client):
        """Test getting empty tasks list."""
        with aioresponses() as m:
            pattern = re.compile(r'.*/tasks/by_telegram/.*')
            m.get(pattern, payload=[])

            result = await client.get_tasks(123456789)

            assert result == []

    @pytest.mark.asyncio
    async def test_get_tasks_error(self, client):
        """Test getting tasks on error."""
        with aioresponses() as m:
            pattern = re.compile(r'.*/tasks/by_telegram/.*')
            m.get(pattern, status=500)

            result = await client.get_tasks(123456789)

            assert result == []

    @pytest.mark.asyncio
    async def test_create_task_success(self, client):
        """Test creating a task."""
        task_response = {
            'id': '01HXYZ123456789ABCDEFGH01',
            'title': 'New Task',
            'description': 'Description',
            'status': 'pending',
            'categories': [],
            'created_at': '2024-01-20T10:00:00Z'
        }

        with aioresponses() as m:
            m.post(
                f'{client.base_url}/tasks/create_for_telegram/',
                payload=task_response,
                status=201
            )

            result = await client.create_task(
                telegram_id=123456789,
                title='New Task',
                description='Description'
            )

            assert result is not None
            assert result['title'] == 'New Task'

    @pytest.mark.asyncio
    async def test_create_task_with_due_date(self, client):
        """Test creating a task with due date."""
        task_response = {
            'id': '01HXYZ123456789ABCDEFGH01',
            'title': 'Task with date',
            'due_date': '2024-12-31T12:00:00Z',
            'categories': [],
            'created_at': '2024-01-20T10:00:00Z'
        }

        with aioresponses() as m:
            m.post(
                f'{client.base_url}/tasks/create_for_telegram/',
                payload=task_response,
                status=201
            )

            result = await client.create_task(
                telegram_id=123456789,
                title='Task with date',
                due_date='2024-12-31T12:00:00'
            )

            assert result is not None
            assert result['due_date'] is not None

    @pytest.mark.asyncio
    async def test_create_task_with_categories(self, client):
        """Test creating a task with categories."""
        task_response = {
            'id': '01HXYZ123456789ABCDEFGH01',
            'title': 'Task with categories',
            'categories': [{'id': 'cat1', 'name': 'Work'}],
            'created_at': '2024-01-20T10:00:00Z'
        }

        with aioresponses() as m:
            m.post(
                f'{client.base_url}/tasks/create_for_telegram/',
                payload=task_response,
                status=201
            )

            result = await client.create_task(
                telegram_id=123456789,
                title='Task with categories',
                category_ids=['cat1']
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_create_task_failure(self, client):
        """Test creating task failure."""
        with aioresponses() as m:
            m.post(
                f'{client.base_url}/tasks/create_for_telegram/',
                status=400
            )

            result = await client.create_task(
                telegram_id=123456789,
                title='Failed Task'
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_get_categories_success(
        self, client, sample_categories_response
    ):
        """Test getting categories list."""
        with aioresponses() as m:
            pattern = re.compile(r'.*/categories/.*')
            m.get(pattern, payload=sample_categories_response)

            result = await client.get_categories(123456789)

            assert result is not None
            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_categories_empty(self, client):
        """Test getting empty categories."""
        with aioresponses() as m:
            pattern = re.compile(r'.*/categories/.*')
            m.get(pattern, payload=[])

            result = await client.get_categories(123456789)

            assert result == []

    @pytest.mark.asyncio
    async def test_create_category_success(self, client):
        """Test creating a category."""
        cat_response = {
            'id': '01HCAT123456789ABCDEFGH01',
            'name': 'New Category',
            'color': '#abcdef'
        }

        with aioresponses() as m:
            m.post(
                f'{client.base_url}/categories/',
                payload=cat_response,
                status=201
            )

            result = await client.create_category(
                user_id='user123',
                name='New Category',
                color='#abcdef'
            )

            assert result is not None
            assert result['name'] == 'New Category'

    @pytest.mark.asyncio
    async def test_update_task_status_success(self, client):
        """Test updating task status."""
        task_response = {
            'id': 'task123',
            'status': 'completed'
        }

        with aioresponses() as m:
            m.patch(
                f'{client.base_url}/tasks/task123/',
                payload=task_response
            )

            result = await client.update_task_status('task123', 'completed')

            assert result is not None
            assert result['status'] == 'completed'

    @pytest.mark.asyncio
    async def test_delete_task_success(self, client):
        """Test deleting a task."""
        with aioresponses() as m:
            m.delete(
                f'{client.base_url}/tasks/task123/',
                status=204
            )

            result = await client.delete_task('task123')

            assert result is True

    @pytest.mark.asyncio
    async def test_delete_task_failure(self, client):
        """Test deleting task failure."""
        with aioresponses() as m:
            m.delete(
                f'{client.base_url}/tasks/task123/',
                status=404
            )

            result = await client.delete_task('task123')

            assert result is False

    @pytest.mark.asyncio
    async def test_request_network_error(self, client):
        """Test handling network errors."""
        import aiohttp
        with aioresponses() as m:
            pattern = re.compile(r'.*/users/by_telegram/.*')
            m.get(
                pattern,
                exception=aiohttp.ClientError('Network error')
            )

            result = await client.get_user_by_telegram(123456789)

            assert result is None


class TestAPIClientSingleton:
    """Test for api_client singleton instance."""

    def test_api_client_instance_exists(self):
        """Test that api_client instance is created."""
        assert api_client is not None
        assert isinstance(api_client, APIClient)
