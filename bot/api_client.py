"""
API client for communication with Django backend.
"""

import os
import logging
from typing import Optional
import aiohttp

logger = logging.getLogger(__name__)

API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000/api')


class APIClient:
    """Async client for ToDo List API."""

    def __init__(self):
        self.base_url = API_BASE_URL

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: dict = None,
        params: dict = None
    ) -> Optional[dict]:
        """Make HTTP request to API."""
        url = f"{self.base_url}/{endpoint}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    url,
                    json=data,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status in (200, 201):
                        return await response.json()
                    elif response.status == 404:
                        return None
                    else:
                        text = await response.text()
                        logger.error(f"API error {response.status}: {text}")
                        return None
        except aiohttp.ClientError as e:
            logger.error(f"Request error: {e}")
            return None

    async def register_user(
        self,
        telegram_id: int,
        username: str
    ) -> Optional[dict]:
        """Register or get existing user by Telegram ID."""
        return await self._request(
            'POST',
            'users/register_telegram/',
            data={'telegram_id': telegram_id, 'username': username}
        )

    async def get_user_by_telegram(self, telegram_id: int) -> Optional[dict]:
        """Get user by Telegram ID."""
        return await self._request(
            'GET',
            'users/by_telegram/',
            params={'telegram_id': telegram_id}
        )

    async def get_tasks(self, telegram_id: int) -> list:
        """Get all tasks for user."""
        result = await self._request(
            'GET',
            'tasks/by_telegram/',
            params={'telegram_id': telegram_id}
        )
        return result if result else []

    async def create_task(
        self,
        telegram_id: int,
        title: str,
        description: str = '',
        due_date: str = None,
        category_ids: list = None
    ) -> Optional[dict]:
        """Create new task for user."""
        data = {
            'telegram_id': telegram_id,
            'title': title,
            'description': description,
        }
        if due_date:
            data['due_date'] = due_date
        if category_ids:
            data['category_ids'] = category_ids

        return await self._request(
            'POST',
            'tasks/create_for_telegram/',
            data=data
        )

    async def get_categories(self, telegram_id: int) -> list:
        """Get all categories for user."""
        result = await self._request(
            'GET',
            'categories/',
            params={'telegram_id': telegram_id}
        )
        return result if result else []

    async def create_category(
        self,
        user_id: str,
        name: str,
        color: str = '#3498db'
    ) -> Optional[dict]:
        """Create new category."""
        return await self._request(
            'POST',
            'categories/',
            data={'user': user_id, 'name': name, 'color': color}
        )

    async def update_task_status(
        self,
        task_id: str,
        status: str
    ) -> Optional[dict]:
        """Update task status."""
        return await self._request(
            'PATCH',
            f'tasks/{task_id}/',
            data={'status': status}
        )

    async def delete_task(self, task_id: str) -> bool:
        """Delete task."""
        url = f"{self.base_url}/tasks/{task_id}/"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(url) as response:
                    return response.status == 204
        except aiohttp.ClientError:
            return False


api_client = APIClient()
