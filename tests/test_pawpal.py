import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Pet, Task


def test_mark_complete_changes_task_status():
    task = Task(task_id="t1", title="Morning Walk", duration_minutes=20)
    assert task.is_completed is False
    task.mark_complete()
    assert task.is_completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Jack", species="dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task(task_id="t1", title="Morning Walk", duration_minutes=20))
    assert len(pet.get_tasks()) == 1
