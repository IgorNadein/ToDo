"""
Command handlers for Telegram bot.
"""

import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram_dialog import DialogManager, StartMode

from api_client import api_client
from states import TaskSG, AddTaskSG

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, dialog_manager: DialogManager):
    """Handle /start command - register user and show welcome message."""
    user = message.from_user
    telegram_id = user.id
    username = user.username or f"user_{telegram_id}"

    # Register user in backend
    result = await api_client.register_user(telegram_id, username)

    if result:
        await message.answer(
            f"👋 Привет, <b>{user.first_name}</b>!\n\n"
            "Я - бот для управления задачами ToDo List.\n\n"
            "📋 <b>Доступные команды:</b>\n"
            "/tasks - Просмотр списка задач\n"
            "/add - Добавить новую задачу\n"
            "/help - Справка по командам"
        )
    else:
        await message.answer(
            "❌ Произошла ошибка при регистрации. "
            "Попробуйте позже или обратитесь к администратору."
        )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    await message.answer(
        "📖 <b>Справка по командам:</b>\n\n"
        "/start - Начать работу с ботом\n"
        "/tasks - Просмотр списка ваших задач\n"
        "/add - Добавить новую задачу\n"
        "/help - Показать эту справку\n\n"
        "💡 <b>Подсказка:</b>\n"
        "При добавлении задачи вы можете указать название, "
        "описание и дату выполнения."
    )


@router.message(Command("tasks"))
async def cmd_tasks(message: Message, dialog_manager: DialogManager):
    """Handle /tasks command - show task list dialog."""
    await dialog_manager.start(TaskSG.list, mode=StartMode.RESET_STACK)


@router.message(Command("add"))
async def cmd_add(message: Message, dialog_manager: DialogManager):
    """Handle /add command - start add task dialog."""
    await dialog_manager.start(AddTaskSG.title, mode=StartMode.RESET_STACK)
