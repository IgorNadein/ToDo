"""
Tests for Telegram bot handlers.
"""

import pytest
from unittest.mock import AsyncMock, patch

from states import TaskSG, AddTaskSG


class TestStartHandler:
    """Tests for /start command handler."""

    @pytest.mark.asyncio
    async def test_start_registers_user(
        self, mock_message, mock_dialog_manager, sample_user_response
    ):
        """Test /start command registers user."""
        from handlers import cmd_start

        with patch('handlers.api_client') as mock_api:
            mock_api.register_user = AsyncMock(return_value=sample_user_response)

            await cmd_start(mock_message, mock_dialog_manager)

            mock_api.register_user.assert_called_once_with(
                mock_message.from_user.id,
                mock_message.from_user.username
            )
            mock_message.answer.assert_called_once()
            # Check welcome message contains user name
            call_args = mock_message.answer.call_args[0][0]
            assert 'Test' in call_args  # first_name

    @pytest.mark.asyncio
    async def test_start_handles_error(
        self, mock_message, mock_dialog_manager
    ):
        """Test /start handles registration error."""
        from handlers import cmd_start

        with patch('handlers.api_client') as mock_api:
            mock_api.register_user = AsyncMock(return_value=None)

            await cmd_start(mock_message, mock_dialog_manager)

            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert 'ошибка' in call_args.lower()


class TestHelpHandler:
    """Tests for /help command handler."""

    @pytest.mark.asyncio
    async def test_help_shows_commands(self, mock_message):
        """Test /help shows available commands."""
        from handlers import cmd_help

        await cmd_help(mock_message)

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert '/start' in call_args
        assert '/tasks' in call_args
        assert '/add' in call_args


class TestTasksHandler:
    """Tests for /tasks command handler."""

    @pytest.mark.asyncio
    async def test_tasks_starts_dialog(
        self, mock_message, mock_dialog_manager
    ):
        """Test /tasks starts task list dialog."""
        from handlers import cmd_tasks

        await cmd_tasks(mock_message, mock_dialog_manager)

        mock_dialog_manager.start.assert_called_once()
        call_args = mock_dialog_manager.start.call_args
        assert call_args[0][0] == TaskSG.list


class TestAddHandler:
    """Tests for /add command handler."""

    @pytest.mark.asyncio
    async def test_add_starts_dialog(
        self, mock_message, mock_dialog_manager
    ):
        """Test /add starts add task dialog."""
        from handlers import cmd_add

        await cmd_add(mock_message, mock_dialog_manager)

        mock_dialog_manager.start.assert_called_once()
        call_args = mock_dialog_manager.start.call_args
        assert call_args[0][0] == AddTaskSG.title
