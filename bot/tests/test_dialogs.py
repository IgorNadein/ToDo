"""
Tests for Aiogram-Dialog dialogs.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from states import TaskSG, AddTaskSG


class TestTaskDialogGetters:
    """Tests for task dialog data getters."""

    @pytest.mark.asyncio
    async def test_get_tasks_data_with_tasks(
        self, mock_dialog_manager, sample_tasks_response
    ):
        """Test getting tasks data when tasks exist."""
        from dialogs import get_tasks_data

        with patch('dialogs.api_client') as mock_api:
            mock_api.get_tasks = AsyncMock(return_value=sample_tasks_response)

            result = await get_tasks_data(mock_dialog_manager)

            assert result['tasks'] == sample_tasks_response
            assert result['tasks_count'] == 2
            assert result['has_tasks'] is True

    @pytest.mark.asyncio
    async def test_get_tasks_data_empty(self, mock_dialog_manager):
        """Test getting tasks data when no tasks."""
        from dialogs import get_tasks_data

        with patch('dialogs.api_client') as mock_api:
            mock_api.get_tasks = AsyncMock(return_value=[])

            result = await get_tasks_data(mock_dialog_manager)

            assert result['tasks'] == []
            assert result['tasks_count'] == 0
            assert result['has_tasks'] is False

    @pytest.mark.asyncio
    async def test_get_task_detail_data(
        self, mock_dialog_manager, sample_tasks_response
    ):
        """Test getting task detail data."""
        from dialogs import get_task_detail_data

        mock_dialog_manager.dialog_data = {
            'selected_task_id': sample_tasks_response[0]['id']
        }

        with patch('dialogs.api_client') as mock_api:
            mock_api.get_tasks = AsyncMock(return_value=sample_tasks_response)

            result = await get_task_detail_data(mock_dialog_manager)

            assert result['task'] is not None
            assert result['title'] == 'Test Task 1'
            assert 'Work' in result['categories']

    @pytest.mark.asyncio
    async def test_get_task_detail_not_found(self, mock_dialog_manager):
        """Test getting task detail when not found."""
        from dialogs import get_task_detail_data

        mock_dialog_manager.dialog_data = {
            'selected_task_id': 'non-existent'
        }

        with patch('dialogs.api_client') as mock_api:
            mock_api.get_tasks = AsyncMock(return_value=[])

            result = await get_task_detail_data(mock_dialog_manager)

            assert result['task'] is None


class TestTaskDialogHandlers:
    """Tests for task dialog event handlers."""

    @pytest.mark.asyncio
    async def test_on_task_selected(self, mock_dialog_manager):
        """Test task selection handler."""
        from dialogs import on_task_selected

        callback = AsyncMock()
        widget = MagicMock()

        await on_task_selected(
            callback, widget, mock_dialog_manager, 'task-id-123'
        )

        assert mock_dialog_manager.dialog_data['selected_task_id'] == 'task-id-123'
        mock_dialog_manager.switch_to.assert_called_once_with(TaskSG.detail)

    @pytest.mark.asyncio
    async def test_on_refresh_tasks(self, mock_dialog_manager):
        """Test refresh tasks handler."""
        from dialogs import on_refresh_tasks

        callback = AsyncMock()
        button = MagicMock()

        await on_refresh_tasks(callback, button, mock_dialog_manager)

        callback.answer.assert_called_once()
        call_args = callback.answer.call_args[0][0]
        assert 'обновлен' in call_args.lower()

    @pytest.mark.asyncio
    async def test_on_complete_task_success(self, mock_dialog_manager):
        """Test complete task handler success."""
        from dialogs import on_complete_task

        callback = AsyncMock()
        button = MagicMock()
        mock_dialog_manager.dialog_data = {'selected_task_id': 'task-123'}

        with patch('dialogs.api_client') as mock_api:
            mock_api.update_task_status = AsyncMock(
                return_value={'status': 'completed'}
            )

            await on_complete_task(callback, button, mock_dialog_manager)

            mock_api.update_task_status.assert_called_with(
                'task-123', 'completed'
            )
            callback.answer.assert_called_once()
            mock_dialog_manager.switch_to.assert_called_with(TaskSG.list)

    @pytest.mark.asyncio
    async def test_on_complete_task_failure(self, mock_dialog_manager):
        """Test complete task handler failure."""
        from dialogs import on_complete_task

        callback = AsyncMock()
        button = MagicMock()
        mock_dialog_manager.dialog_data = {'selected_task_id': 'task-123'}

        with patch('dialogs.api_client') as mock_api:
            mock_api.update_task_status = AsyncMock(return_value=None)

            await on_complete_task(callback, button, mock_dialog_manager)

            call_args = callback.answer.call_args[0][0]
            assert 'ошибка' in call_args.lower()


class TestAddTaskDialogHandlers:
    """Tests for add task dialog handlers."""

    @pytest.mark.asyncio
    async def test_on_title_entered(self, mock_dialog_manager):
        """Test title input handler."""
        from dialogs import on_title_entered

        message = AsyncMock()
        widget = MagicMock()

        await on_title_entered(message, widget, mock_dialog_manager, 'My Task')

        assert mock_dialog_manager.dialog_data['title'] == 'My Task'
        mock_dialog_manager.switch_to.assert_called_with(AddTaskSG.description)

    @pytest.mark.asyncio
    async def test_on_description_entered(self, mock_dialog_manager):
        """Test description input handler."""
        from dialogs import on_description_entered

        message = AsyncMock()
        widget = MagicMock()

        await on_description_entered(
            message, widget, mock_dialog_manager, 'Task description'
        )

        assert mock_dialog_manager.dialog_data['description'] == 'Task description'
        mock_dialog_manager.switch_to.assert_called_with(AddTaskSG.due_date)

    @pytest.mark.asyncio
    async def test_on_skip_description(self, mock_dialog_manager):
        """Test skip description handler."""
        from dialogs import on_skip_description

        callback = AsyncMock()
        button = MagicMock()

        await on_skip_description(callback, button, mock_dialog_manager)

        assert mock_dialog_manager.dialog_data['description'] == ''
        mock_dialog_manager.switch_to.assert_called_with(AddTaskSG.due_date)

    @pytest.mark.asyncio
    async def test_on_due_date_entered_valid(self, mock_dialog_manager):
        """Test valid due date input."""
        from dialogs import on_due_date_entered

        message = AsyncMock()
        widget = MagicMock()

        await on_due_date_entered(
            message, widget, mock_dialog_manager, '25.12.2024 15:30'
        )

        assert 'due_date' in mock_dialog_manager.dialog_data
        mock_dialog_manager.switch_to.assert_called_with(AddTaskSG.confirm)

    @pytest.mark.asyncio
    async def test_on_due_date_entered_date_only(self, mock_dialog_manager):
        """Test date-only input without time."""
        from dialogs import on_due_date_entered

        message = AsyncMock()
        widget = MagicMock()

        await on_due_date_entered(
            message, widget, mock_dialog_manager, '25.12.2024'
        )

        assert 'due_date' in mock_dialog_manager.dialog_data

    @pytest.mark.asyncio
    async def test_on_due_date_entered_invalid(self, mock_dialog_manager):
        """Test invalid due date input."""
        from dialogs import on_due_date_entered

        message = AsyncMock()
        widget = MagicMock()

        await on_due_date_entered(
            message, widget, mock_dialog_manager, 'invalid date'
        )

        message.answer.assert_called_once()
        call_args = message.answer.call_args[0][0]
        assert 'неверный' in call_args.lower()

    @pytest.mark.asyncio
    async def test_on_skip_due_date(self, mock_dialog_manager):
        """Test skip due date handler."""
        from dialogs import on_skip_due_date

        callback = AsyncMock()
        button = MagicMock()

        await on_skip_due_date(callback, button, mock_dialog_manager)

        assert mock_dialog_manager.dialog_data['due_date'] is None
        mock_dialog_manager.switch_to.assert_called_with(AddTaskSG.confirm)

    @pytest.mark.asyncio
    async def test_get_confirm_data(self, mock_dialog_manager):
        """Test confirmation data getter."""
        from dialogs import get_confirm_data

        mock_dialog_manager.dialog_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'due_date': '2024-12-25T15:30:00'
        }

        result = await get_confirm_data(mock_dialog_manager)

        assert result['title'] == 'Test Task'
        assert result['description'] == 'Test Description'
        assert '25.12.2024' in result['due_date']

    @pytest.mark.asyncio
    async def test_get_confirm_data_no_due_date(self, mock_dialog_manager):
        """Test confirmation data without due date."""
        from dialogs import get_confirm_data

        mock_dialog_manager.dialog_data = {
            'title': 'Test Task',
            'description': '',
            'due_date': None
        }

        result = await get_confirm_data(mock_dialog_manager)

        assert result['due_date'] == '—'
        assert result['description'] == '—'

    @pytest.mark.asyncio
    async def test_on_confirm_task_success(self, mock_callback):
        """Test task creation on confirm."""
        from dialogs import on_confirm_task

        mock_dialog_manager = AsyncMock()
        mock_dialog_manager.dialog_data = {
            'title': 'Confirmed Task',
            'description': 'Description',
            'due_date': '2024-12-25T15:30:00'
        }

        with patch('dialogs.api_client') as mock_api:
            mock_api.create_task = AsyncMock(
                return_value={'id': 'new-task', 'title': 'Confirmed Task'}
            )

            await on_confirm_task(
                mock_callback, MagicMock(), mock_dialog_manager
            )

            mock_api.create_task.assert_called_once()
            mock_callback.message.answer.assert_called()
            mock_dialog_manager.done.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_confirm_task_failure(self, mock_callback):
        """Test task creation failure on confirm."""
        from dialogs import on_confirm_task

        mock_dialog_manager = AsyncMock()
        mock_dialog_manager.dialog_data = {
            'title': 'Failed Task',
            'description': '',
            'due_date': None
        }

        with patch('dialogs.api_client') as mock_api:
            mock_api.create_task = AsyncMock(return_value=None)

            await on_confirm_task(
                mock_callback, MagicMock(), mock_dialog_manager
            )

            call_args = mock_callback.message.answer.call_args[0][0]
            assert 'ошибка' in call_args.lower()


class TestFormatTaskDate:
    """Tests for format_task_date helper function."""

    def test_format_valid_date(self):
        """Test formatting valid ISO date."""
        from dialogs import format_task_date

        result = format_task_date('2024-01-15T10:30:00Z')

        assert '15.01.2024' in result
        assert '10:30' in result

    def test_format_invalid_date(self):
        """Test formatting invalid date."""
        from dialogs import format_task_date

        result = format_task_date('invalid')

        assert result == '—'

    def test_format_none_date(self):
        """Test formatting None date."""
        from dialogs import format_task_date

        result = format_task_date(None)

        assert result == '—'
