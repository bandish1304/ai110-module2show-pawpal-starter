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

    title: str
    duration_minutes: int
    priority: str = "medium"          # "low" | "medium" | "high"
    category: str = "general"
    frequency: str = "daily"
    preferred_time: str = "anytime"
    is_required: bool = False
    notes: str = ""

    def is_high_priority(self) -> bool:
        pass

    def is_required_task(self) -> bool:
        pass

    def fits_time_limit(self, minutes: int) -> bool:
        pass

    def get_priority_score(self) -> int:
        pass

    def update_task(self, **kwargs) -> None:
        pass

    def describe(self) -> str:
        pass


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

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_title: str) -> None:
        pass

    def get_tasks(self) -> list[Task]:
        pass

    def get_required_tasks(self) -> list[Task]:
        pass

    def get_pet_summary(self) -> str:
        pass


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
    ):
        self.name = name
        self.available_minutes_per_day = available_minutes_per_day
        self.preferred_schedule = preferred_schedule
        self.task_preferences: list[str] = task_preferences or []
        self.max_tasks_per_day = max_tasks_per_day
        self.notes = notes

    def update_available_time(self, minutes: int) -> None:
        pass

    def set_preferences(self, preferences: list[str]) -> None:
        pass

    def add_preference(self, task_type: str) -> None:
        pass

    def remove_preference(self, task_type: str) -> None:
        pass

    def can_do_task(self, task: Task) -> bool:
        pass

    def get_summary(self) -> str:
        pass


# ---------------------------------------------------------------------------
# Scheduler — orchestrates the daily plan
# ---------------------------------------------------------------------------

class Scheduler:
    """Selects and orders tasks to build a daily care plan."""

    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.tasks: list[Task] = []
        self.time_budget: int = 0
        self.scheduled_tasks: list[Task] = []
        self.unscheduled_tasks: list[Task] = []

    def generate_schedule(self) -> list[Task]:
        pass

    def rank_tasks(self) -> list[Task]:
        pass

    def filter_tasks(self) -> list[Task]:
        pass

    def sort_tasks(self) -> list[Task]:
        pass

    def fit_tasks_into_day(self) -> None:
        pass

    def explain_schedule(self) -> str:
        pass
