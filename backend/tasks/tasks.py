"""
Celery tasks for ToDo List application.
Задачи для отправки уведомлений при наступлении даты исполнения.
"""

import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone


@shared_task
def send_task_notification(task_id):
    """
    Отправляет уведомление пользователю в Telegram о задаче.
    """
    from .models import Task

    try:
        task = Task.objects.select_related('user').get(id=task_id)
    except Task.DoesNotExist:
        return f"Task {task_id} not found"

    if not task.user.telegram_id:
        return f"User {task.user.username} has no telegram_id"

    if task.notification_sent:
        return f"Notification already sent for task {task_id}"

    # Формируем сообщение
    message = (
        f"⏰ <b>Напоминание о задаче!</b>\n\n"
        f"📋 <b>{task.title}</b>\n"
    )
    if task.description:
        message += f"📝 {task.description}\n"
    if task.due_date:
        message += f"📅 Срок: {task.due_date.strftime('%d.%m.%Y %H:%M')}\n"

    categories = task.categories.all()
    if categories:
        category_names = ', '.join([c.name for c in categories])
        message += f"🏷 Категории: {category_names}"

    # Отправляем сообщение через Telegram Bot API
    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        return "TELEGRAM_BOT_TOKEN not configured"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': task.user.telegram_id,
        'text': message,
        'parse_mode': 'HTML'
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            task.notification_sent = True
            task.save(update_fields=['notification_sent'])
            return f"Notification sent for task {task_id}"
        else:
            return f"Failed to send notification: {response.text}"
    except requests.RequestException as e:
        return f"Error sending notification: {str(e)}"


@shared_task
def check_due_tasks():
    """
    Периодическая задача для проверки задач с наступившей датой исполнения.
    Запускается каждую минуту и отправляет уведомления.
    """
    from .models import Task

    now = timezone.now()

    # Находим задачи, у которых наступила дата исполнения и уведомление не отправлено
    tasks = Task.objects.filter(
        due_date__lte=now,
        notification_sent=False,
        status__in=['pending', 'in_progress']
    ).select_related('user')

    sent_count = 0
    for task in tasks:
        if task.user.telegram_id:
            send_task_notification.delay(task.id)
            sent_count += 1

    return f"Scheduled {sent_count} notifications"
