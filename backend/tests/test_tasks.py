"""
Tests for Celery tasks: send_task_notification, check_due_tasks.
"""

from unittest.mock import patch, MagicMock
from django.utils import timezone
from datetime import timedelta

from tasks.models import Task
from tasks.tasks import send_task_notification, check_due_tasks


class TestSendTaskNotification:
    """Tests for send_task_notification Celery task."""

    @patch('tasks.tasks.requests.post')
    def test_send_notification_success(
        self, mock_post, overdue_task, db
    ):
        """Test successful notification sending."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        with patch('tasks.tasks.settings') as mock_settings:
            mock_settings.TELEGRAM_BOT_TOKEN = 'test-token'

            result = send_task_notification(overdue_task.id)

            assert 'Notification sent' in result
            overdue_task.refresh_from_db()
            assert overdue_task.notification_sent is True

    @patch('tasks.tasks.requests.post')
    def test_send_notification_api_error(
        self, mock_post, overdue_task, db
    ):
        """Test notification when API returns error."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = 'Bad Request'
        mock_post.return_value = mock_response

        with patch('tasks.tasks.settings') as mock_settings:
            mock_settings.TELEGRAM_BOT_TOKEN = 'test-token'

            result = send_task_notification(overdue_task.id)

            assert 'Failed to send' in result
            overdue_task.refresh_from_db()
            assert overdue_task.notification_sent is False

    def test_send_notification_task_not_found(self, db):
        """Test notification for non-existent task."""
        result = send_task_notification('non-existent-id')
        assert 'not found' in result

    def test_send_notification_user_no_telegram(
        self, user_without_telegram, db
    ):
        """Test notification when user has no telegram_id."""
        task = Task.objects.create(
            title='No Telegram Task',
            user=user_without_telegram,
            due_date=timezone.now() - timedelta(hours=1)
        )

        result = send_task_notification(task.id)
        assert 'has no telegram_id' in result

    def test_send_notification_already_sent(
        self, task_with_notification_sent, db
    ):
        """Test skipping already notified task."""
        result = send_task_notification(task_with_notification_sent.id)
        assert 'already sent' in result

    def test_send_notification_no_token(self, overdue_task, db):
        """Test notification without bot token configured."""
        with patch('tasks.tasks.settings') as mock_settings:
            mock_settings.TELEGRAM_BOT_TOKEN = ''

            result = send_task_notification(overdue_task.id)

            assert 'not configured' in result

    @patch('tasks.tasks.requests.post')
    def test_send_notification_request_exception(
        self, mock_post, overdue_task, db
    ):
        """Test notification when request raises exception."""
        import requests
        mock_post.side_effect = requests.RequestException('Network error')

        with patch('tasks.tasks.settings') as mock_settings:
            mock_settings.TELEGRAM_BOT_TOKEN = 'test-token'

            result = send_task_notification(overdue_task.id)

            assert 'Error sending' in result

    @patch('tasks.tasks.requests.post')
    def test_notification_message_format(
        self, mock_post, overdue_task, category, db
    ):
        """Test notification message contains required info."""
        overdue_task.categories.add(category)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        with patch('tasks.tasks.settings') as mock_settings:
            mock_settings.TELEGRAM_BOT_TOKEN = 'test-token'

            send_task_notification(overdue_task.id)

            # Check the message content
            call_args = mock_post.call_args
            payload = call_args.kwargs.get('json') or call_args[1].get('json')
            message = payload['text']

            assert overdue_task.title in message
            assert 'Напоминание' in message


class TestCheckDueTasks:
    """Tests for check_due_tasks periodic task."""

    @patch('tasks.tasks.send_task_notification.delay')
    def test_check_due_tasks_schedules_notifications(
        self, mock_delay, overdue_task, db
    ):
        """Test that overdue tasks trigger notifications."""
        result = check_due_tasks()

        assert mock_delay.called
        mock_delay.assert_called_with(overdue_task.id)
        assert 'Scheduled 1 notifications' in result

    @patch('tasks.tasks.send_task_notification.delay')
    def test_check_due_tasks_skips_completed(
        self, mock_delay, completed_task, db
    ):
        """Test that completed tasks are skipped."""
        # Make the completed task overdue
        completed_task.due_date = timezone.now() - timedelta(hours=1)
        completed_task.notification_sent = False
        completed_task.save()

        result = check_due_tasks()

        assert not mock_delay.called
        assert 'Scheduled 0' in result

    @patch('tasks.tasks.send_task_notification.delay')
    def test_check_due_tasks_skips_already_notified(
        self, mock_delay, task_with_notification_sent, db
    ):
        """Test that already notified tasks are skipped."""
        check_due_tasks()

        assert not mock_delay.called

    @patch('tasks.tasks.send_task_notification.delay')
    def test_check_due_tasks_skips_future_tasks(
        self, mock_delay, task, db
    ):
        """Test that future tasks are not notified."""
        # task fixture has due_date in the future
        check_due_tasks()

        assert not mock_delay.called

    @patch('tasks.tasks.send_task_notification.delay')
    def test_check_due_tasks_skips_no_telegram_user(
        self, mock_delay, user_without_telegram, db
    ):
        """Test that tasks from users without telegram are skipped."""
        Task.objects.create(
            title='No Telegram User Task',
            user=user_without_telegram,
            due_date=timezone.now() - timedelta(hours=1),
            notification_sent=False
        )

        result = check_due_tasks()

        assert not mock_delay.called
        assert 'Scheduled 0' in result

    @patch('tasks.tasks.send_task_notification.delay')
    def test_check_due_tasks_multiple_overdue(
        self, mock_delay, user, db
    ):
        """Test scheduling notifications for multiple overdue tasks."""
        # Create 3 overdue tasks
        for i in range(3):
            Task.objects.create(
                title=f'Overdue Task {i}',
                user=user,
                due_date=timezone.now() - timedelta(hours=i + 1),
                notification_sent=False
            )

        result = check_due_tasks()

        assert mock_delay.call_count == 3
        assert 'Scheduled 3' in result
