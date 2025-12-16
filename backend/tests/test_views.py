"""
Tests for API views: UserViewSet, CategoryViewSet, TaskViewSet.
"""

from rest_framework import status


class TestHealthCheck:
    """Tests for health check endpoint."""

    def test_health_check(self, api_client, db):
        """Test health check returns ok."""
        response = api_client.get('/api/health/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'status': 'ok'}


class TestUserViewSet:
    """Tests for User API endpoints."""

    def test_list_users(self, api_client, user, db):
        """Test listing all users."""
        response = api_client.get('/api/users/')
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_user(self, api_client, user, db):
        """Test retrieving a specific user."""
        response = api_client.get(f'/api/users/{user.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username

    def test_register_telegram_new_user(self, api_client, db):
        """Test registering new user via Telegram."""
        data = {
            'telegram_id': 999888777,
            'username': 'telegram_new_user'
        }
        response = api_client.post(
            '/api/users/register_telegram/',
            data,
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['telegram_id'] == 999888777

    def test_register_telegram_existing_user(self, api_client, user, db):
        """Test registering existing Telegram user returns user."""
        data = {
            'telegram_id': user.telegram_id,
            'username': 'different_name'
        }
        response = api_client.post(
            '/api/users/register_telegram/',
            data,
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user.id

    def test_register_telegram_without_id(self, api_client, db):
        """Test registering without telegram_id returns error."""
        response = api_client.post(
            '/api/users/register_telegram/',
            {'username': 'notelid'},
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_telegram_auto_username(self, api_client, db):
        """Test auto-generating username from telegram_id."""
        data = {'telegram_id': 112233445}
        response = api_client.post(
            '/api/users/register_telegram/',
            data,
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert 'telegram_112233445' in response.data['username']

    def test_by_telegram(self, api_client, user, db):
        """Test getting user by telegram_id."""
        response = api_client.get(
            '/api/users/by_telegram/',
            {'telegram_id': user.telegram_id}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user.id

    def test_by_telegram_not_found(self, api_client, db):
        """Test 404 when telegram_id not found."""
        response = api_client.get(
            '/api/users/by_telegram/',
            {'telegram_id': 999999999}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_by_telegram_missing_param(self, api_client, db):
        """Test error when telegram_id param missing."""
        response = api_client.get('/api/users/by_telegram/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestCategoryViewSet:
    """Tests for Category API endpoints."""

    def test_list_categories(self, api_client, category, db):
        """Test listing all categories."""
        response = api_client.get('/api/categories/')
        assert response.status_code == status.HTTP_200_OK

    def test_list_categories_by_user_id(self, api_client, category, user, db):
        """Test filtering categories by user_id."""
        response = api_client.get(
            '/api/categories/',
            {'user_id': user.id}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_list_categories_by_telegram_id(self, api_client, category, user, db):
        """Test filtering categories by telegram_id."""
        response = api_client.get(
            '/api/categories/',
            {'telegram_id': user.telegram_id}
        )
        assert response.status_code == status.HTTP_200_OK

    def test_create_category(self, api_client, user, db):
        """Test creating a category."""
        data = {
            'name': 'API Category',
            'color': '#123456',
            'user': user.id
        }
        response = api_client.post('/api/categories/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'API Category'

    def test_retrieve_category(self, api_client, category, db):
        """Test retrieving a specific category."""
        response = api_client.get(f'/api/categories/{category.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == category.name

    def test_update_category(self, api_client, category, db):
        """Test updating a category."""
        data = {'name': 'Updated Category'}
        response = api_client.patch(
            f'/api/categories/{category.id}/',
            data,
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Category'

    def test_delete_category(self, api_client, category, db):
        """Test deleting a category."""
        response = api_client.delete(f'/api/categories/{category.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestTaskViewSet:
    """Tests for Task API endpoints."""

    def test_list_tasks(self, api_client, task, db):
        """Test listing all tasks."""
        response = api_client.get('/api/tasks/')
        assert response.status_code == status.HTTP_200_OK

    def test_list_tasks_by_user_id(self, api_client, task, user, db):
        """Test filtering tasks by user_id."""
        response = api_client.get('/api/tasks/', {'user_id': user.id})
        assert response.status_code == status.HTTP_200_OK

    def test_list_tasks_by_telegram_id(self, api_client, task, user, db):
        """Test filtering tasks by telegram_id."""
        response = api_client.get(
            '/api/tasks/',
            {'telegram_id': user.telegram_id}
        )
        assert response.status_code == status.HTTP_200_OK

    def test_list_tasks_by_status(self, api_client, multiple_tasks, db):
        """Test filtering tasks by status."""
        response = api_client.get('/api/tasks/', {'status': 'pending'})
        assert response.status_code == status.HTTP_200_OK
        # Handle paginated response
        results = response.data.get('results', response.data)
        for task in results:
            assert task['status'] == 'pending'

    def test_create_task(self, api_client, user, db):
        """Test creating a task."""
        data = {
            'title': 'API Task',
            'description': 'Created via API',
            'user': user.id
        }
        response = api_client.post('/api/tasks/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'API Task'

    def test_retrieve_task(self, api_client, task, db):
        """Test retrieving a specific task."""
        response = api_client.get(f'/api/tasks/{task.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == task.title

    def test_update_task(self, api_client, task, db):
        """Test updating a task."""
        data = {'title': 'Updated Task', 'status': 'completed'}
        response = api_client.patch(
            f'/api/tasks/{task.id}/',
            data,
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Task'
        assert response.data['status'] == 'completed'

    def test_delete_task(self, api_client, task, db):
        """Test deleting a task."""
        response = api_client.delete(f'/api/tasks/{task.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_by_telegram(self, api_client, task, user, db):
        """Test getting tasks by telegram_id."""
        response = api_client.get(
            '/api/tasks/by_telegram/',
            {'telegram_id': user.telegram_id}
        )
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_by_telegram_missing_param(self, api_client, db):
        """Test error when telegram_id param missing."""
        response = api_client.get('/api/tasks/by_telegram/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_for_telegram(self, api_client, user, db):
        """Test creating task for Telegram user."""
        data = {
            'telegram_id': user.telegram_id,
            'title': 'Telegram Task',
            'description': 'Created from bot'
        }
        response = api_client.post(
            '/api/tasks/create_for_telegram/',
            data,
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Telegram Task'

    def test_create_for_telegram_missing_id(self, api_client, db):
        """Test error when telegram_id missing."""
        data = {'title': 'No Telegram ID'}
        response = api_client.post(
            '/api/tasks/create_for_telegram/',
            data,
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_for_telegram_user_not_found(self, api_client, db):
        """Test 404 when Telegram user not found."""
        data = {
            'telegram_id': 999999999,
            'title': 'Unknown User Task'
        }
        response = api_client.post(
            '/api/tasks/create_for_telegram/',
            data,
            format='json'
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_task_categories_in_response(self, api_client, task, db):
        """Test that task response includes categories."""
        response = api_client.get(f'/api/tasks/{task.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert 'categories' in response.data
        assert len(response.data['categories']) > 0

    def test_task_created_at_in_list(self, api_client, task, db):
        """Test that created_at is included in list response."""
        response = api_client.get('/api/tasks/')
        assert response.status_code == status.HTTP_200_OK
        # Handle paginated response
        results = response.data.get('results', response.data)
        for item in results:
            assert 'created_at' in item
