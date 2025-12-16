"""
Aiogram-Dialog dialogs for bot interaction.
"""

import logging
from datetime import datetime
from typing import Any

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import (
    Button, Row, ScrollingGroup, Select, Back, Cancel
)
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput

from api_client import api_client
from states import TaskSG, AddTaskSG

logger = logging.getLogger(__name__)

dialog_router = Router()


# ============== Task List Dialog ==============

async def get_tasks_data(dialog_manager: DialogManager, **kwargs) -> dict:
    """Get tasks data for the dialog."""
    event = dialog_manager.event
    telegram_id = event.from_user.id

    tasks = await api_client.get_tasks(telegram_id)

    return {
        "tasks": tasks,
        "tasks_count": len(tasks),
        "has_tasks": len(tasks) > 0
    }


def format_task_date(created_at: str) -> str:
    """Format task creation date."""
    try:
        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        return dt.strftime('%d.%m.%Y %H:%M')
    except (ValueError, AttributeError):
        return "—"


async def on_task_selected(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    item_id: str
):
    """Handle task selection."""
    dialog_manager.dialog_data["selected_task_id"] = item_id
    await dialog_manager.switch_to(TaskSG.detail)


async def get_task_detail_data(
    dialog_manager: DialogManager,
    **kwargs
) -> dict:
    """Get selected task details."""
    task_id = dialog_manager.dialog_data.get("selected_task_id")
    event = dialog_manager.event
    telegram_id = event.from_user.id

    tasks = await api_client.get_tasks(telegram_id)
    task = next((t for t in tasks if t['id'] == task_id), None)

    if task:
        categories = task.get('categories', [])
        category_names = ', '.join([c['name'] for c in categories]) if categories else '—'
        created_at = format_task_date(task.get('created_at', ''))
        due_date = task.get('due_date')
        if due_date:
            due_date = format_task_date(due_date)
        else:
            due_date = '—'

        status_map = {
            'pending': '⏳ В ожидании',
            'in_progress': '🔄 В процессе',
            'completed': '✅ Завершена'
        }

        return {
            "task": task,
            "title": task.get('title', ''),
            "description": task.get('description', '') or '—',
            "status": status_map.get(task.get('status'), task.get('status')),
            "categories": category_names,
            "created_at": created_at,
            "due_date": due_date
        }

    return {"task": None}


async def on_refresh_tasks(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager
):
    """Refresh task list."""
    await callback.answer("🔄 Список обновлен")


async def on_complete_task(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager
):
    """Mark task as completed."""
    task_id = dialog_manager.dialog_data.get("selected_task_id")
    result = await api_client.update_task_status(task_id, 'completed')
    if result:
        await callback.answer("✅ Задача завершена!")
    else:
        await callback.answer("❌ Ошибка при обновлении")
    await dialog_manager.switch_to(TaskSG.list)


task_dialog = Dialog(
    Window(
        Const("📋 <b>Ваши задачи:</b>\n"),
        Format(
            "Всего задач: {tasks_count}",
            when=F["has_tasks"]
        ),
        Const(
            "У вас пока нет задач.\n"
            "Используйте /add для добавления.",
            when=~F["has_tasks"]
        ),
        ScrollingGroup(
            Select(
                Format(
                    "📌 {item[title]} | 🕐 {item[created_at]}"
                ),
                id="task_select",
                items="tasks",
                item_id_getter=lambda x: x['id'],
                on_click=on_task_selected,
            ),
            id="tasks_scroll",
            width=1,
            height=5,
            when=F["has_tasks"]
        ),
        Row(
            Button(
                Const("🔄 Обновить"),
                id="refresh",
                on_click=on_refresh_tasks
            ),
            Cancel(Const("❌ Закрыть")),
        ),
        state=TaskSG.list,
        getter=get_tasks_data,
    ),
    Window(
        Format("<b>📌 {title}</b>\n"),
        Format("📝 <b>Описание:</b> {description}\n"),
        Format("📊 <b>Статус:</b> {status}\n"),
        Format("🏷 <b>Категории:</b> {categories}\n"),
        Format("📅 <b>Создана:</b> {created_at}\n"),
        Format("⏰ <b>Срок:</b> {due_date}"),
        Row(
            Button(
                Const("✅ Завершить"),
                id="complete",
                on_click=on_complete_task
            ),
            Back(Const("◀️ Назад")),
        ),
        state=TaskSG.detail,
        getter=get_task_detail_data,
    ),
)

dialog_router.include_router(task_dialog)


# ============== Add Task Dialog ==============

async def on_title_entered(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str
):
    """Handle task title input."""
    dialog_manager.dialog_data["title"] = text
    await dialog_manager.switch_to(AddTaskSG.description)


async def on_description_entered(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str
):
    """Handle task description input."""
    dialog_manager.dialog_data["description"] = text
    await dialog_manager.switch_to(AddTaskSG.due_date)


async def on_skip_description(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager
):
    """Skip description input."""
    dialog_manager.dialog_data["description"] = ""
    await dialog_manager.switch_to(AddTaskSG.due_date)


async def on_due_date_entered(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str
):
    """Handle due date input."""
    # Try to parse date in format DD.MM.YYYY HH:MM or DD.MM.YYYY
    try:
        if ' ' in text:
            dt = datetime.strptime(text, '%d.%m.%Y %H:%M')
        else:
            dt = datetime.strptime(text, '%d.%m.%Y')

        dialog_manager.dialog_data["due_date"] = dt.isoformat()
        await dialog_manager.switch_to(AddTaskSG.confirm)
    except ValueError:
        await message.answer(
            "❌ Неверный формат даты. "
            "Используйте ДД.ММ.ГГГГ или ДД.ММ.ГГГГ ЧЧ:ММ"
        )


async def on_skip_due_date(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager
):
    """Skip due date input."""
    dialog_manager.dialog_data["due_date"] = None
    await dialog_manager.switch_to(AddTaskSG.confirm)


async def get_confirm_data(dialog_manager: DialogManager, **kwargs) -> dict:
    """Get data for confirmation window."""
    data = dialog_manager.dialog_data
    due_date = data.get("due_date")
    if due_date:
        try:
            dt = datetime.fromisoformat(due_date)
            due_date = dt.strftime('%d.%m.%Y %H:%M')
        except ValueError:
            due_date = "—"
    else:
        due_date = "—"

    return {
        "title": data.get("title", ""),
        "description": data.get("description", "") or "—",
        "due_date": due_date
    }


async def on_confirm_task(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager
):
    """Create task on confirmation."""
    data = dialog_manager.dialog_data
    telegram_id = callback.from_user.id

    result = await api_client.create_task(
        telegram_id=telegram_id,
        title=data.get("title", ""),
        description=data.get("description", ""),
        due_date=data.get("due_date")
    )

    if result:
        await callback.message.answer("✅ Задача успешно создана!")
    else:
        await callback.message.answer("❌ Ошибка при создании задачи")

    await dialog_manager.done()


add_task_dialog = Dialog(
    Window(
        Const("📝 <b>Создание новой задачи</b>\n"),
        Const("Введите название задачи:"),
        TextInput(
            id="title_input",
            on_success=on_title_entered,
        ),
        Cancel(Const("❌ Отмена")),
        state=AddTaskSG.title,
    ),
    Window(
        Const("📝 <b>Описание задачи</b>\n"),
        Const("Введите описание (или нажмите Пропустить):"),
        TextInput(
            id="description_input",
            on_success=on_description_entered,
        ),
        Row(
            Button(
                Const("⏭ Пропустить"),
                id="skip_desc",
                on_click=on_skip_description
            ),
            Cancel(Const("❌ Отмена")),
        ),
        state=AddTaskSG.description,
    ),
    Window(
        Const("📅 <b>Срок выполнения</b>\n"),
        Const("Введите дату (ДД.ММ.ГГГГ или ДД.ММ.ГГГГ ЧЧ:ММ):"),
        TextInput(
            id="due_date_input",
            on_success=on_due_date_entered,
        ),
        Row(
            Button(
                Const("⏭ Пропустить"),
                id="skip_date",
                on_click=on_skip_due_date
            ),
            Back(Const("◀️ Назад")),
        ),
        Cancel(Const("❌ Отмена")),
        state=AddTaskSG.due_date,
    ),
    Window(
        Const("✅ <b>Подтверждение</b>\n"),
        Format("📌 <b>Название:</b> {title}\n"),
        Format("📝 <b>Описание:</b> {description}\n"),
        Format("📅 <b>Срок:</b> {due_date}\n"),
        Const("\nСоздать задачу?"),
        Row(
            Button(
                Const("✅ Создать"),
                id="confirm",
                on_click=on_confirm_task
            ),
            Back(Const("◀️ Назад")),
        ),
        Cancel(Const("❌ Отмена")),
        state=AddTaskSG.confirm,
        getter=get_confirm_data,
    ),
)

dialog_router.include_router(add_task_dialog)
