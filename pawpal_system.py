from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str          # "high", "medium", "low"
    task_type: str         # "walk", "feeding", "medication", "appointment", "grooming", "enrichment"
    is_recurring: bool = False
    recurrence_interval: str = "daily"   # "daily", "weekly", "as_needed"

    def to_dict(self) -> dict:
        pass


@dataclass
class Pet:
    name: str
    species: str           # "dog", "cat", "other"
    age: int
    breed: str = "unknown"
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, title: str) -> None:
        pass

    def get_tasks(self) -> List[Task]:
        pass


@dataclass
class Owner:
    name: str
    email: str
    available_minutes_per_day: int = 120
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, name: str) -> None:
        pass

    def get_pets(self) -> List[Pet]:
        pass


@dataclass
class ScheduledTask:
    task: Task
    start_time: str   # "HH:MM" 24-hour format
    end_time: str     # "HH:MM" 24-hour format
    reason: str = ""

    def to_dict(self) -> dict:
        pass


class Scheduler:
    def __init__(self, owner: Owner, date: str, start_time: str = "08:00"):
        self.owner = owner
        self.date = date           # "YYYY-MM-DD"
        self.start_time = start_time

    def generate_schedule(self, pet: Pet) -> List[ScheduledTask]:
        pass

    def sort_tasks(self, tasks: List[Task]) -> List[Task]:
        pass

    def detect_conflicts(self, schedule: List[ScheduledTask]) -> List[tuple]:
        pass

    def explain_plan(self, schedule: List[ScheduledTask]) -> str:
        pass
