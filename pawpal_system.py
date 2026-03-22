"""
pawpal_system.py
----------------
Logic layer for PawPal+.
Class skeletons for Owner, Pet, Task, and Scheduler.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta


# ---------------------------------------------------------------------------
# Task — uses dataclass for clean attribute declaration
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single pet care activity."""

    task_id: str
    title: str
    duration_minutes: int
    priority: str = "medium"          # "low" | "medium" | "high"
    category: str = "general"
    frequency: str = "daily"
    preferred_time: str = "anytime"
    time: str = ""
    due_date: date = field(default_factory=date.today)
    is_required: bool = False
    start_minute: int | None = None
    notes: str = ""
    description: str = ""
    is_completed: bool = False
    last_completed_day: int | None = None
    last_completed_on: date | None = None

    def __post_init__(self) -> None:
        """Normalize and validate task attributes after initialization."""
        self.task_id = self.task_id.strip()
        self.title = self.title.strip()
        self.priority = self.priority.strip().lower()
        self.category = self.category.strip().lower()
        self.frequency = self.frequency.strip().lower()
        self.preferred_time = self.preferred_time.strip().lower()
        self.time = self.time.strip()
        if not self.task_id:
            raise ValueError("task_id cannot be empty")
        if not self.title:
            raise ValueError("title cannot be empty")
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be greater than 0")
        if self.time:
            pieces = self.time.split(":")
            if len(pieces) != 2 or not all(part.isdigit() for part in pieces):
                raise ValueError("time must be in HH:MM format")
            hours, minutes = int(pieces[0]), int(pieces[1])
            if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
                raise ValueError("time must be in HH:MM format")
        if self.start_minute is not None and self.start_minute < 0:
            raise ValueError("start_minute cannot be negative")
        if self.priority not in {"low", "medium", "high"}:
            raise ValueError("priority must be 'low', 'medium', or 'high'")
        if not isinstance(self.due_date, date):
            raise ValueError("due_date must be a date")

    def is_high_priority(self) -> bool:
        """Return whether this task is marked as high priority."""
        return self.priority == "high"

    def is_required_task(self) -> bool:
        """Return whether this task is required."""
        return self.is_required

    def fits_time_limit(self, minutes: int) -> bool:
        """Return whether the task fits within the given minute limit."""
        return minutes >= 0 and self.duration_minutes <= minutes

    def get_priority_score(self) -> int:
        """Compute a weighted score used to rank tasks for scheduling."""
        if self.is_completed:
            return 0

        priority_scores = {"low": 1, "medium": 2, "high": 3}
        frequency_scores = {"daily": 2, "weekly": 1}
        score = priority_scores.get(self.priority, 0)
        score += frequency_scores.get(self.frequency, 0)
        if self.is_required:
            score += 3
        return score

    def mark_complete(
        self,
        day_index: int | None = None,
        completed_on: date | None = None,
    ) -> None:
        """Mark this task complete and stamp completion metadata."""
        self.is_completed = True
        if completed_on is not None and day_index is not None:
            raise ValueError("Provide either day_index or completed_on, not both")

        if completed_on is not None:
            self.last_completed_on = completed_on
            return

        if day_index is not None:
            if day_index < 0:
                raise ValueError("day_index cannot be negative")
            self.last_completed_day = day_index
            self.last_completed_on = date.today() + timedelta(days=day_index)
            return

        self.last_completed_on = date.today()

    def is_due_on_day(self, day_index: int) -> bool:
        """Return whether this task should be considered due on a given day."""
        if day_index < 0:
            raise ValueError("day_index cannot be negative")

        check_date = date.today() + timedelta(days=day_index)
        return (not self.is_completed) and self.due_date <= check_date

    def update_task(self, **kwargs) -> None:
        """Update task fields dynamically and re-validate task data."""
        allowed_fields = set(self.__dataclass_fields__)
        for key, value in kwargs.items():
            if key not in allowed_fields:
                raise AttributeError(f"Unknown task field: {key}")
            setattr(self, key, value)
        self.__post_init__()

    def describe(self) -> str:
        """Return a concise, human-readable description of this task."""
        status = "completed" if self.is_completed else "pending"
        details = [
            self.title,
            f"{self.duration_minutes} min",
            self.priority,
            self.frequency,
            status,
        ]
        if self.description:
            details.insert(1, self.description)
        return " | ".join(details)


# ---------------------------------------------------------------------------
# Pet — uses dataclass for clean attribute declaration
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """A pet and its associated care needs."""

    name: str
    species: str
    breed: str = ""
    age: int = 0
    energy_level: str = "medium"      # "low" | "medium" | "high"
    medical_needs: str = ""
    care_tasks: list[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Normalize and validate pet attributes after initialization."""
        self.name = self.name.strip()
        self.species = self.species.strip().lower()
        self.breed = self.breed.strip()
        self.energy_level = self.energy_level.strip().lower()
        if not self.name:
            raise ValueError("name cannot be empty")
        if not self.species:
            raise ValueError("species cannot be empty")
        if self.age < 0:
            raise ValueError("age cannot be negative")

    def add_task(self, task: Task) -> None:
        """Add a new care task to this pet, enforcing unique task IDs."""
        if self.get_task_by_id(task.task_id) is not None:
            raise ValueError(f"Task with id '{task.task_id}' already exists for {self.name}")
        self.care_tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a care task from this pet by task ID."""
        task = self.get_task_by_id(task_id)
        if task is None:
            raise ValueError(f"Task with id '{task_id}' was not found for {self.name}")
        self.care_tasks.remove(task)

    def get_task_by_id(self, task_id: str) -> Task | None:
        """Return the task matching the provided ID, if present."""
        for task in self.care_tasks:
            if task.task_id == task_id:
                return task
        return None

    def get_tasks(self) -> list[Task]:
        """Return a copy of this pet's task list."""
        return list(self.care_tasks)

    def get_required_tasks(self) -> list[Task]:
        """Return all required care tasks for this pet."""
        return [task for task in self.care_tasks if task.is_required_task()]

    def get_pet_summary(self) -> str:
        """Return a short summary of this pet and its task load."""
        return (
            f"{self.name} ({self.species}) - {len(self.care_tasks)} task(s), "
            f"energy: {self.energy_level}"
        )


# ---------------------------------------------------------------------------
# Owner — plain class (holds preferences + mutable state)
# ---------------------------------------------------------------------------

class Owner:
    """The pet owner and their scheduling constraints."""

    def __init__(
        self,
        name: str,
        available_minutes_per_day: int = 60,
        preferred_schedule: str = "morning",
        task_preferences: list[str] | None = None,
        max_tasks_per_day: int = 5,
        notes: str = "",
        pets: list[Pet] | None = None,
    ):
        self.name = name
        self.available_minutes_per_day = available_minutes_per_day
        self.preferred_schedule = preferred_schedule.strip().lower()
        self.task_preferences: list[str] = []
        self.max_tasks_per_day = max_tasks_per_day
        self.notes = notes
        self.pets: list[Pet] = pets or []
        self.set_preferences(task_preferences or [])

    def update_available_time(self, minutes: int) -> None:
        """Set the owner's daily available minutes for pet care."""
        if minutes < 0:
            raise ValueError("available_minutes_per_day cannot be negative")
        self.available_minutes_per_day = minutes

    def set_preferences(self, preferences: list[str]) -> None:
        """Replace task preferences with normalized, unique values."""
        normalized_preferences: list[str] = []
        for preference in preferences:
            normalized = preference.strip().lower()
            if normalized and normalized not in normalized_preferences:
                normalized_preferences.append(normalized)
        self.task_preferences = normalized_preferences

    def add_preference(self, task_type: str) -> None:
        """Add a normalized task preference if it is not already present."""
        normalized = task_type.strip().lower()
        if normalized and normalized not in self.task_preferences:
            self.task_preferences.append(normalized)

    def remove_preference(self, task_type: str) -> None:
        """Remove a normalized task preference when it exists."""
        normalized = task_type.strip().lower()
        if normalized in self.task_preferences:
            self.task_preferences.remove(normalized)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner, enforcing unique pet names."""
        if self.get_pet(pet.name) is not None:
            raise ValueError(f"Pet '{pet.name}' already exists for {self.name}")
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet from this owner by name."""
        pet = self.get_pet(pet_name)
        if pet is None:
            raise ValueError(f"Pet '{pet_name}' was not found for {self.name}")
        self.pets.remove(pet)

    def get_pet(self, pet_name: str) -> Pet | None:
        """Return the pet matching the provided name, if present."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.strip().lower():
                return pet
        return None

    def get_pets(self) -> list[Pet]:
        """Return a copy of the owner's pet list."""
        return list(self.pets)

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks across all pets owned by this owner."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks())
        return tasks

    def can_do_task(self, task: Task) -> bool:
        """Return whether a task is incomplete and within daily time limits."""
        return not task.is_completed and task.duration_minutes <= self.available_minutes_per_day

    def get_summary(self) -> str:
        """Return a short summary of owner constraints and managed pets."""
        return (
            f"{self.name} can spend {self.available_minutes_per_day} min/day, "
            f"prefers {self.preferred_schedule}, and manages {len(self.pets)} pet(s)"
        )


# ---------------------------------------------------------------------------
# Scheduler — orchestrates the daily plan
# ---------------------------------------------------------------------------

class Scheduler:
    """Selects and orders tasks to build a daily care plan."""

    def __init__(self, owner: Owner, pet: Pet | None = None):
        self.owner = owner
        self.pet = pet
        self.tasks: list[Task] = []
        self.time_budget: int = 0
        self.scheduled_tasks: list[Task] = []
        self.unscheduled_tasks: list[Task] = []
        self.selection_reasons: dict[str, str] = {}
        self.task_pet_lookup: dict[str, str] = {}
        self.schedule_date: date = date.today()

    TIME_SLOT_ORDER = {
        "morning": 0,
        "afternoon": 1,
        "evening": 2,
        "night": 3,
        "anytime": 4,
    }

    def refresh_inputs(self) -> None:
        """Reload pets, tasks, and scheduling state from current owner inputs."""
        self.time_budget = self.owner.available_minutes_per_day
        self.scheduled_tasks = []
        self.unscheduled_tasks = []
        self.selection_reasons = {}
        self.task_pet_lookup = {}

        pets = [self.pet] if self.pet is not None else self.owner.get_pets()
        tasks: list[Task] = []
        for pet in pets:
            for task in pet.get_tasks():
                tasks.append(task)
                self.task_pet_lookup[task.task_id] = pet.name
        self.tasks = tasks

    def generate_schedule(self, day_index: int = 0) -> list[Task]:
        """Build and return the list of tasks due on the target day.

        The target day is computed as ``today + day_index`` and stored in
        ``self.schedule_date``. Eligibility checks (including recurrence due dates)
        are then evaluated against that date.
        """
        self.schedule_date = date.today() + timedelta(days=day_index)
        self.refresh_inputs()
        self.fit_tasks_into_day()
        return list(self.scheduled_tasks)

    def prepare_recurring_tasks(self, day_index: int = 0) -> None:
        """Backward-compatible no-op (recurrence now creates next instances)."""
        _ = day_index

    def mark_task_complete(
        self,
        task_id: str,
        completed_on: date | None = None,
    ) -> Task | None:
        """Complete a task and optionally create its next recurring instance.

        For tasks with ``daily`` or ``weekly`` frequency, this method creates a new
        pending Task due on ``completed_on + timedelta(days=1|7)`` and adds it to the
        same pet. Non-recurring tasks are just marked complete.

        Returns:
            The newly created recurring task when applicable, otherwise ``None``.
        """
        completion_date = completed_on or date.today()
        pets = [self.pet] if self.pet is not None else self.owner.get_pets()

        for pet in pets:
            task = pet.get_task_by_id(task_id)
            if task is None:
                continue

            task.mark_complete(completed_on=completion_date)

            if task.frequency not in {"daily", "weekly"}:
                return None

            days_to_add = 1 if task.frequency == "daily" else 7
            next_due_date = completion_date + timedelta(days=days_to_add)
            next_task = self._create_next_recurring_task(task, pet, next_due_date)
            pet.add_task(next_task)
            return next_task

        raise ValueError(f"Task with id '{task_id}' was not found")

    def rank_tasks(self) -> list[Task]:
        """Return eligible tasks sorted by ranking score and tie-breakers."""
        ranked_tasks = self.filter_tasks()
        return sorted(
            ranked_tasks,
            key=lambda task: (
                -self._get_task_rank(task),
                task.duration_minutes,
                task.title.lower(),
            ),
        )

    def filter_tasks(self) -> list[Task]:
        """Return tasks eligible for scheduling and record skipped reasons."""
        eligible_tasks: list[Task] = []
        for task in self.tasks:
            if task.is_completed:
                self.unscheduled_tasks.append(task)
                self.selection_reasons[task.task_id] = "Skipped because the task is already completed."
                continue
            if not self.owner.can_do_task(task):
                self.unscheduled_tasks.append(task)
                self.selection_reasons[task.task_id] = (
                    "Skipped because the task exceeds the owner's daily time limit."
                )
                continue
            if task.due_date > self.schedule_date:
                self.unscheduled_tasks.append(task)
                self.selection_reasons[task.task_id] = (
                    "Skipped because this recurring task is not due yet."
                )
                continue
            eligible_tasks.append(task)
        return eligible_tasks

    def sort_tasks(self) -> list[Task]:
        """Return tasks ordered according to scheduling priority rules."""
        return self.rank_tasks()

    def sort_tasks_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Sort tasks by coarse time buckets and deterministic tie-breakers.

        Ordering priority:
        1) preferred slot (morning/afternoon/evening/night/anytime),
        2) explicit ``start_minute`` when present,
        3) shorter duration,
        4) title alphabetically.
        """
        tasks_to_sort = list(tasks) if tasks is not None else list(self.tasks)
        return sorted(
            tasks_to_sort,
            key=lambda task: (
                self.TIME_SLOT_ORDER.get(task.preferred_time, 99),
                task.start_minute if task.start_minute is not None else 10_000,
                task.duration_minutes,
                task.title.lower(),
            ),
        )

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Sort tasks by explicit ``HH:MM`` values.

        Tasks without a ``time`` value are pushed to the end by assigning them a
        large sentinel tuple key ``(99, 99)``.
        """
        tasks_to_sort = list(tasks) if tasks is not None else list(self.tasks)
        return sorted(
            tasks_to_sort,
            key=lambda task: (
                tuple(int(part) for part in task.time.split(":")) if task.time else (99, 99),
                task.title.lower(),
            ),
        )

    def filter_tasks_by_pet_status(
        self,
        pet_name: str | None = None,
        status: str = "all",
    ) -> list[Task]:
        """Filter tasks by optional pet name and completion status.

        Args:
            pet_name: When provided, include only tasks for that pet.
            status: One of ``all``, ``completed``, or ``pending``.

        Returns:
            A filtered list preserving original task order.
        """
        if not self.tasks:
            self.refresh_inputs()

        normalized_pet = pet_name.strip().lower() if pet_name else None
        normalized_status = status.strip().lower()
        if normalized_status not in {"all", "completed", "pending"}:
            raise ValueError("status must be 'all', 'completed', or 'pending'")

        filtered_tasks: list[Task] = []
        for task in self.tasks:
            owner_pet_name = self.task_pet_lookup.get(task.task_id, "").lower()
            if normalized_pet and owner_pet_name != normalized_pet:
                continue
            if normalized_status == "completed" and not task.is_completed:
                continue
            if normalized_status == "pending" and task.is_completed:
                continue
            filtered_tasks.append(task)
        return filtered_tasks

    def filter_by(self, pet_name: str | None = None, status: str = "all") -> list[Task]:
        """Alias for filtering tasks by pet name and completion status."""
        return self.filter_tasks_by_pet_status(pet_name=pet_name, status=status)

    def fit_tasks_into_day(self) -> None:
        """Select ranked tasks that fit time and daily task-count constraints."""
        remaining_minutes = self.time_budget
        ranked_tasks = self.sort_tasks()

        for task in ranked_tasks:
            if len(self.scheduled_tasks) >= self.owner.max_tasks_per_day:
                self.unscheduled_tasks.append(task)
                self.selection_reasons[task.task_id] = (
                    "Skipped because the daily task limit was reached."
                )
                continue

            if task.duration_minutes > remaining_minutes:
                self.unscheduled_tasks.append(task)
                self.selection_reasons[task.task_id] = (
                    "Skipped because there was not enough time remaining in the day."
                )
                continue

            conflict_task = self._find_conflicting_task(task)
            if conflict_task is not None:
                conflicting_title = conflict_task.title
                self.unscheduled_tasks.append(task)
                self.selection_reasons[task.task_id] = (
                    f"Skipped because it conflicts with '{conflicting_title}'."
                )
                continue

            self.scheduled_tasks.append(task)
            remaining_minutes -= task.duration_minutes
            self.selection_reasons[task.task_id] = self._build_selection_reason(task)

    def detect_conflicts(self, tasks: list[Task] | None = None) -> list[tuple[Task, Task]]:
        """Return all overlapping task pairs based on computed start/end windows.

        The method builds a timeline of tasks with concrete start times (from either
        ``start_minute`` or parsed ``HH:MM``), sorts by start time, and scans forward
        with early-break once no further overlap is possible.
        """
        if not self.tasks:
            self.refresh_inputs()

        tasks_to_check = list(tasks) if tasks is not None else list(self.tasks)
        timeline: list[tuple[Task, int, int]] = []
        for task in tasks_to_check:
            start_minute = self._get_task_start_minute(task)
            if start_minute is None:
                continue
            end_minute = start_minute + task.duration_minutes
            timeline.append((task, start_minute, end_minute))
        timeline.sort(key=lambda entry: entry[1])

        conflicts: list[tuple[Task, Task]] = []
        for index, (current_task, current_start, current_end) in enumerate(timeline):
            for candidate_task, candidate_start, _candidate_end in timeline[index + 1:]:
                if candidate_start >= current_end:
                    break
                conflicts.append((current_task, candidate_task))
        return conflicts

    def get_conflict_warnings(self, tasks: list[Task] | None = None) -> list[str]:
        """Create human-readable warnings for each detected conflict pair.

        This is intentionally lightweight: it reports overlaps as warnings without
        raising exceptions or mutating task state.
        """
        if not self.tasks:
            self.refresh_inputs()

        warnings: list[str] = []
        for task_a, task_b in self.detect_conflicts(tasks):
            pet_a = self.task_pet_lookup.get(task_a.task_id, "Unknown pet")
            pet_b = self.task_pet_lookup.get(task_b.task_id, "Unknown pet")
            conflict_scope = "same pet" if pet_a == pet_b else "different pets"
            start_a = self._format_task_start(task_a)
            start_b = self._format_task_start(task_b)
            warnings.append(
                f"Conflict warning ({conflict_scope}): {pet_a} - {task_a.title} ({start_a}) overlaps with "
                f"{pet_b} - {task_b.title} ({start_b})."
            )
        return warnings

    def explain_schedule(self) -> str:
        """Return a readable explanation of selected and skipped tasks."""
        if not self.scheduled_tasks and not self.unscheduled_tasks:
            self.generate_schedule()

        lines = [
            f"Schedule for {self.owner.name}",
            f"Time budget: {self.time_budget} minutes",
            f"Scheduled tasks: {len(self.scheduled_tasks)}",
        ]

        if self.scheduled_tasks:
            lines.append("Selected tasks:")
            for task in self.scheduled_tasks:
                pet_name = self.task_pet_lookup.get(task.task_id, "Unknown pet")
                lines.append(
                    f"- {pet_name}: {task.title} ({task.duration_minutes} min) - "
                    f"{self.selection_reasons.get(task.task_id, 'Selected') }"
                )

        if self.unscheduled_tasks:
            lines.append("Skipped tasks:")
            for task in self.unscheduled_tasks:
                pet_name = self.task_pet_lookup.get(task.task_id, "Unknown pet")
                lines.append(
                    f"- {pet_name}: {task.title} - "
                    f"{self.selection_reasons.get(task.task_id, 'Not scheduled') }"
                )

        return "\n".join(lines)

    def _get_task_rank(self, task: Task) -> int:
        """Calculate composite rank score for a task."""
        score = task.get_priority_score()
        if task.preferred_time == self.owner.preferred_schedule:
            score += 2
        if task.preferred_time == "anytime":
            score += 1
        if self._matches_preferences(task):
            score += 1
        return score

    def _matches_preferences(self, task: Task) -> bool:
        """Return whether a task matches any owner preference token."""
        if not self.owner.task_preferences:
            return False
        return any(
            option in {task.category, task.frequency, task.title.lower()}
            for option in self.owner.task_preferences
        )

    def _build_selection_reason(self, task: Task) -> str:
        """Build a short explanation describing why a task was selected."""
        reasons: list[str] = []
        if task.is_required_task():
            reasons.append("it is required")
        if task.is_high_priority():
            reasons.append("it is high priority")
        if task.preferred_time == self.owner.preferred_schedule:
            reasons.append("it matches the owner's preferred schedule")
        if self._matches_preferences(task):
            reasons.append("it matches the owner's task preferences")
        if not reasons:
            reasons.append("it fits within the remaining time budget")
        return "Selected because " + ", ".join(reasons) + "."

    def _find_conflicting_task(self, task: Task) -> Task | None:
        """Return the first already-scheduled task that conflicts with the candidate."""
        if self._get_task_start_minute(task) is None:
            return None
        for scheduled_task in self.scheduled_tasks:
            if self._tasks_conflict(task, scheduled_task):
                return scheduled_task
        return None

    @staticmethod
    def _tasks_conflict(task_a: Task, task_b: Task) -> bool:
        """Return whether two tasks overlap after normalizing their start times."""
        start_a = Scheduler._get_task_start_minute(task_a)
        start_b = Scheduler._get_task_start_minute(task_b)
        if start_a is None or start_b is None:
            return False

        task_a_end = start_a + task_a.duration_minutes
        task_b_end = start_b + task_b.duration_minutes
        return start_a < task_b_end and start_b < task_a_end

    @staticmethod
    def _get_task_start_minute(task: Task) -> int | None:
        """Resolve a task's start minute from ``start_minute`` or ``HH:MM`` text."""
        if task.start_minute is not None:
            return task.start_minute
        if not task.time:
            return None
        hours_text, minutes_text = task.time.split(":")
        return int(hours_text) * 60 + int(minutes_text)

    @staticmethod
    def _format_task_start(task: Task) -> str:
        """Return a display-friendly time label used in conflict warnings."""
        if task.time:
            return task.time
        start_minute = Scheduler._get_task_start_minute(task)
        if start_minute is None:
            return "unspecified"
        hours = start_minute // 60
        minutes = start_minute % 60
        return f"{hours:02d}:{minutes:02d}"

    @staticmethod
    def _create_next_recurring_task(task: Task, pet: Pet, next_due_date: date) -> Task:
        """Clone a recurring task into a new pending task due on ``next_due_date``.

        The method also ensures a unique ``task_id`` within the pet by appending
        a numeric suffix when needed.
        """
        base_task_id = f"{task.task_id}-next-{next_due_date.isoformat()}"
        candidate_task_id = base_task_id
        counter = 2
        while pet.get_task_by_id(candidate_task_id) is not None:
            candidate_task_id = f"{base_task_id}-{counter}"
            counter += 1

        return Task(
            task_id=candidate_task_id,
            title=task.title,
            duration_minutes=task.duration_minutes,
            priority=task.priority,
            category=task.category,
            frequency=task.frequency,
            preferred_time=task.preferred_time,
            time=task.time,
            due_date=next_due_date,
            is_required=task.is_required,
            start_minute=task.start_minute,
            notes=task.notes,
            description=task.description,
            is_completed=False,
        )
