import sys
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Pet, Task
from pawpal_system import Owner, Scheduler


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


def test_sort_tasks_by_time_orders_morning_before_evening():
    owner = Owner(name="Ben", available_minutes_per_day=60)
    pet = Pet(name="Jack", species="dog")
    pet.add_task(
        Task(
            task_id="evening-task",
            title="Evening Walk",
            duration_minutes=20,
            preferred_time="evening",
        )
    )
    pet.add_task(
        Task(
            task_id="morning-task",
            title="Breakfast",
            duration_minutes=10,
            preferred_time="morning",
        )
    )
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    sorted_tasks = scheduler.sort_tasks_by_time()

    assert [task.task_id for task in sorted_tasks] == ["morning-task", "evening-task"]


def test_filter_tasks_by_pet_and_status_returns_only_pending_for_pet():
    owner = Owner(name="Ben", available_minutes_per_day=60)
    dog = Pet(name="Jack", species="dog")
    cat = Pet(name="Leah", species="cat")

    dog_done = Task(task_id="dog-done", title="Done", duration_minutes=5)
    dog_done.mark_complete()
    dog_pending = Task(task_id="dog-pending", title="Pending", duration_minutes=5)
    cat_pending = Task(task_id="cat-pending", title="Cat Pending", duration_minutes=5)

    dog.add_task(dog_done)
    dog.add_task(dog_pending)
    cat.add_task(cat_pending)
    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    filtered = scheduler.filter_tasks_by_pet_status(pet_name="Jack", status="pending")

    assert [task.task_id for task in filtered] == ["dog-pending"]


def test_mark_task_complete_creates_next_daily_occurrence():
    owner = Owner(name="Ben", available_minutes_per_day=20)
    pet = Pet(name="Jack", species="dog")
    recurring = Task(
        task_id="daily-med",
        title="Medication",
        duration_minutes=5,
        frequency="daily",
    )
    pet.add_task(recurring)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete("daily-med", completed_on=date(2026, 3, 22))

    assert recurring.is_completed is True
    assert next_task is not None
    assert next_task.task_id.startswith("daily-med-next-")
    assert next_task.is_completed is False
    assert next_task.due_date == date(2026, 3, 23)

    scheduled_today = scheduler.generate_schedule(day_index=0)
    scheduled_tomorrow = scheduler.generate_schedule(day_index=1)

    assert [task.task_id for task in scheduled_today] == []
    assert [task.task_id for task in scheduled_tomorrow] == [next_task.task_id]


def test_conflict_detection_skips_overlapping_tasks():
    owner = Owner(name="Ben", available_minutes_per_day=60, max_tasks_per_day=5)
    pet = Pet(name="Jack", species="dog")
    pet.add_task(
        Task(
            task_id="task-a",
            title="Task A",
            duration_minutes=30,
            priority="high",
            start_minute=60,
        )
    )
    pet.add_task(
        Task(
            task_id="task-b",
            title="Task B",
            duration_minutes=30,
            priority="high",
            start_minute=75,
        )
    )
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduled = scheduler.generate_schedule()

    scheduled_ids = {task.task_id for task in scheduled}
    assert len(scheduled_ids) == 1
    assert scheduled_ids in ({"task-a"}, {"task-b"})

    conflict_pairs = scheduler.detect_conflicts(owner.get_all_tasks())
    assert len(conflict_pairs) == 1


def test_sort_by_time_orders_hhmm_strings_correctly():
    owner = Owner(name="Ben", available_minutes_per_day=60)
    pet = Pet(name="Jack", species="dog")
    pet.add_task(Task(task_id="t-late", title="Late", duration_minutes=10, time="18:30"))
    pet.add_task(Task(task_id="t-early", title="Early", duration_minutes=10, time="07:15"))
    pet.add_task(Task(task_id="t-mid", title="Mid", duration_minutes=10, time="12:00"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    sorted_tasks = scheduler.sort_by_time()

    assert [task.task_id for task in sorted_tasks] == ["t-early", "t-mid", "t-late"]


def test_filter_by_alias_filters_completed_tasks_for_specific_pet():
    owner = Owner(name="Ben", available_minutes_per_day=60)
    dog = Pet(name="Jack", species="dog")
    cat = Pet(name="Leah", species="cat")

    done_task = Task(task_id="dog-done", title="Done", duration_minutes=5)
    done_task.mark_complete()
    dog.add_task(done_task)
    dog.add_task(Task(task_id="dog-pending", title="Pending", duration_minutes=5))
    cat.add_task(Task(task_id="cat-done", title="Cat Done", duration_minutes=5, is_completed=True))

    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    filtered = scheduler.filter_by(pet_name="Jack", status="completed")

    assert [task.task_id for task in filtered] == ["dog-done"]


def test_get_conflict_warnings_returns_messages_without_crashing():
    owner = Owner(name="Ben", available_minutes_per_day=120, max_tasks_per_day=10)
    dog = Pet(name="Jack", species="dog")
    cat = Pet(name="Leah", species="cat")

    dog.add_task(Task(task_id="dog-a", title="Dog Task A", duration_minutes=30, time="09:00"))
    dog.add_task(Task(task_id="dog-b", title="Dog Task B", duration_minutes=20, time="09:15"))
    cat.add_task(Task(task_id="cat-a", title="Cat Task A", duration_minutes=30, time="09:10"))

    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner)
    scheduler.refresh_inputs()
    warnings = scheduler.get_conflict_warnings()

    assert len(warnings) >= 2
    assert any("same pet" in warning for warning in warnings)
    assert any("different pets" in warning for warning in warnings)
