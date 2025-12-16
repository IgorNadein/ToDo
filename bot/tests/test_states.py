"""
Tests for states module.
"""

from states import TaskSG, AddTaskSG


class TestTaskSG:
    """Tests for TaskSG states group."""

    def test_task_list_state_exists(self):
        """Test that list state exists."""
        assert hasattr(TaskSG, 'list')

    def test_task_detail_state_exists(self):
        """Test that detail state exists."""
        assert hasattr(TaskSG, 'detail')

    def test_states_are_unique(self):
        """Test that states are unique."""
        assert TaskSG.list != TaskSG.detail


class TestAddTaskSG:
    """Tests for AddTaskSG states group."""

    def test_title_state_exists(self):
        """Test that title state exists."""
        assert hasattr(AddTaskSG, 'title')

    def test_description_state_exists(self):
        """Test that description state exists."""
        assert hasattr(AddTaskSG, 'description')

    def test_due_date_state_exists(self):
        """Test that due_date state exists."""
        assert hasattr(AddTaskSG, 'due_date')

    def test_confirm_state_exists(self):
        """Test that confirm state exists."""
        assert hasattr(AddTaskSG, 'confirm')

    def test_all_states_unique(self):
        """Test that all states are unique."""
        states = [
            AddTaskSG.title,
            AddTaskSG.description,
            AddTaskSG.due_date,
            AddTaskSG.confirm
        ]
        assert len(states) == len(set(states))
