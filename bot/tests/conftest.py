"""
Pytest configuration and fixtures for Telegram bot tests.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_user():
    """Create a mock Telegram user."""
    user = MagicMock()
    user.id = 123456789
    user.username = 'testuser'
    user.first_name = 'Test'
    return user


@pytest.fixture
def mock_message(mock_user):
    """Create a mock Telegram message."""
    message = AsyncMock()
    message.from_user = mock_user
    message.answer = AsyncMock()
    message.text = '/start'
    return message


@pytest.fixture
def mock_callback(mock_user):
    """Create a mock callback query."""
    callback = AsyncMock()
    callback.from_user = mock_user
    callback.answer = AsyncMock()
    callback.message = AsyncMock()
    callback.message.answer = AsyncMock()
    return callback


@pytest.fixture
def mock_dialog_manager():
    """Create a mock DialogManager."""
    manager = AsyncMock()
    manager.dialog_data = {}
    manager.event = MagicMock()
    manager.event.from_user = MagicMock()
    manager.event.from_user.id = 123456789
    manager.start = AsyncMock()
    manager.switch_to = AsyncMock()
    manager.done = AsyncMock()
    return manager


@pytest.fixture
def sample_user_response():
    """Sample API response for user."""
    return {
        'id': '01HXYZ123456789ABCDEFGHJK',
        'username': 'testuser',
        'email': '',
        'telegram_id': 123456789,
        'date_joined': '2024-01-01T00:00:00Z'
    }


@pytest.fixture
def sample_tasks_response():
    """Sample API response for tasks list."""
    return [
        {
            'id': '01HXYZ123456789ABCDEFGH01',
            'title': 'Test Task 1',
            'description': 'Description 1',
            'status': 'pending',
            'due_date': '2024-12-31T12:00:00Z',
            'categories': [
                {'id': '01HCAT123456789ABCDEFGH01', 'name': 'Work', 'color': '#ff0000'}
            ],
            'created_at': '2024-01-15T10:30:00Z'
        },
        {
            'id': '01HXYZ123456789ABCDEFGH02',
            'title': 'Test Task 2',
            'description': '',
            'status': 'in_progress',
            'due_date': None,
            'categories': [],
            'created_at': '2024-01-16T14:45:00Z'
        }
    ]


@pytest.fixture
def sample_categories_response():
    """Sample API response for categories list."""
    return [
        {'id': '01HCAT123456789ABCDEFGH01', 'name': 'Work', 'color': '#ff0000'},
        {'id': '01HCAT123456789ABCDEFGH02', 'name': 'Personal', 'color': '#00ff00'}
    ]
