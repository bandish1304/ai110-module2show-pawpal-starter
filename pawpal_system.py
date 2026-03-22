"""
pawpal_system.py
----------------
Logic layer for PawPal+.
Class skeletons for Owner, Pet, Task, and Scheduler.
"""

from __future__ import annotations
from dataclasses import dataclass, field


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
    is_required: bool = False
    notes: str = ""
    description: str = ""
    is_completed: bool = False

    def __post_init__(self) -> None:
        """Normalize and validate task attributes after initialization."""
        self.task_id = self.task_id.strip()
        self.title = self.title.strip()
        self.priority = self.priority.strip().lower()
        self.category = self.category.strip().lower()
        self.frequency = self.frequency.strip().lower()
        self.preferred_time = self.preferred_time.strip().lower()
        if not self.task_id:
            raise ValueError("task_id cannot be empty")
        if not self.title:
            raise ValueError("title cannot be empty")
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be greater than 0")
        if self.priority not in {"low", "medium", "high"}:
            raise ValueError("priority must be 'low', 'medium', or 'high'")

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

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

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

    def generate_schedule(self) -> list[Task]:
        """Build and return the list of tasks scheduled for today."""
        self.refresh_inputs()
        self.fit_tasks_into_day()
        return list(self.scheduled_tasks)

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
            eligible_tasks.append(task)
        return eligible_tasks

    def sort_tasks(self) -> list[Task]:
        """Return tasks ordered according to scheduling priority rules."""
        return self.rank_tasks()

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

            self.scheduled_tasks.append(task)
            remaining_minutes -= task.duration_minutes
            self.selection_reasons[task.task_id] = self._build_selection_reason(task)

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
