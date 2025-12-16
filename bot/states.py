"""
Dialog states for Aiogram-Dialog.
"""

from aiogram.fsm.state import State, StatesGroup


class TaskSG(StatesGroup):
    """States for task list dialog."""
    list = State()
    detail = State()


class AddTaskSG(StatesGroup):
    """States for add task dialog."""
    title = State()
    description = State()
    due_date = State()
    confirm = State()
