from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta, date as date_type
from typing import List, Optional, Tuple


PRIORITY_ORDER = {"high": 3, "medium": 2, "low": 1}


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str           # "high", "medium", "low"
    task_type: str          # "walk", "feeding", "medication", "appointment", "grooming", "enrichment"
    is_recurring: bool = False
    recurrence_interval: str = "daily"  # "daily", "weekly", "as_needed"
    completed: bool = False
    preferred_time: str = "08:00"       # HH:MM; earliest preferred start in the day
    due_date: str = ""                  # YYYY-MM-DD; empty = any day

    def mark_complete(self) -> Optional["Task"]:
        """Mark done; return a next-occurrence Task if recurring, else None."""
        self.completed = True
        if self.is_recurring and self.recurrence_interval != "as_needed":
            return self._next_occurrence()
        return None

    def _next_occurrence(self) -> "Task":
        """Build a fresh copy of this task scheduled for the next recurrence date."""
        base = date_type.fromisoformat(self.due_date) if self.due_date else date_type.today()
        delta = timedelta(days=1) if self.recurrence_interval == "daily" else timedelta(weeks=1)
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            task_type=self.task_type,
            is_recurring=self.is_recurring,
            recurrence_interval=self.recurrence_interval,
            completed=False,
            preferred_time=self.preferred_time,
            due_date=str(base + delta),
        )

    def to_dict(self) -> dict:
        """Return a plain-dict representation of this task."""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "task_type": self.task_type,
            "is_recurring": self.is_recurring,
            "recurrence_interval": self.recurrence_interval,
            "completed": self.completed,
            "preferred_time": self.preferred_time,
            "due_date": self.due_date,
        }


@dataclass
class Pet:
    name: str
    species: str    # "dog", "cat", "other"
    age: int
    breed: str = "unknown"
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove the first task whose title matches."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        return list(self.tasks)


@dataclass
class Owner:
    name: str
    email: str
    available_minutes_per_day: int = 120
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's roster."""
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        """Remove the first pet whose name matches."""
        self.pets = [p for p in self.pets if p.name != name]

    def get_pets(self) -> List[Pet]:
        """Return all pets owned by this owner."""
        return list(self.pets)


@dataclass
class ScheduledTask:
    task: Task
    start_time: str     # "HH:MM" 24-hour
    end_time: str       # "HH:MM" 24-hour
    reason: str = ""

    def to_dict(self) -> dict:
        """Return a plain-dict representation suitable for display or JSON."""
        return {
            "title": self.task.title,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_minutes": self.task.duration_minutes,
            "priority": self.task.priority,
            "task_type": self.task.task_type,
            "reason": self.reason,
        }


class Scheduler:
    def __init__(self, owner: Owner, date: str, start_time: str = "08:00"):
        self.owner = owner
        self.date = date            # "YYYY-MM-DD"
        self.start_time = start_time

    def sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort by priority descending; break ties by duration ascending (shorter first)."""
        return sorted(
            tasks,
            key=lambda t: (-PRIORITY_ORDER.get(t.priority, 0), t.duration_minutes),
        )

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by preferred_time ascending; within the same slot, by priority descending."""
        return sorted(
            tasks,
            key=lambda t: (t.preferred_time, -PRIORITY_ORDER.get(t.priority, 0)),
        )

    def filter_tasks(
        self,
        pet: Pet,
        *,
        completed: Optional[bool] = None,
        task_type: Optional[str] = None,
    ) -> List[Task]:
        """Return a pet's tasks filtered by completion status and/or task type."""
        tasks = pet.get_tasks()
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        if task_type is not None:
            tasks = [t for t in tasks if t.task_type == task_type]
        return tasks

    def generate_schedule(self, pet: Pet) -> List[ScheduledTask]:
        """Assign time slots honoring each task's preferred_time and the owner's budget."""
        # Primary sort: preferred_time; secondary: priority (so high-pri tasks win ties)
        tasks = self.sort_by_time(pet.get_tasks())
        schedule: List[ScheduledTask] = []
        current_dt = datetime.strptime(f"{self.date} {self.start_time}", "%Y-%m-%d %H:%M")
        remaining = self.owner.available_minutes_per_day

        for task in tasks:
            if task.duration_minutes > remaining:
                continue  # skip — won't fit, keep checking smaller tasks

            # Don't start before preferred_time
            preferred_dt = datetime.strptime(
                f"{self.date} {task.preferred_time}", "%Y-%m-%d %H:%M"
            )
            task_start = max(current_dt, preferred_dt)
            task_end = task_start + timedelta(minutes=task.duration_minutes)

            reason = (
                f"Preferred at {task.preferred_time}; "
                f"starts at {task_start.strftime('%H:%M')}; "
                f"priority={task.priority}; "
                f"{remaining} min remaining."
            )
            schedule.append(
                ScheduledTask(
                    task=task,
                    start_time=task_start.strftime("%H:%M"),
                    end_time=task_end.strftime("%H:%M"),
                    reason=reason,
                )
            )
            current_dt = task_end
            remaining -= task.duration_minutes

        return schedule

    def detect_conflicts(
        self, schedule: List[ScheduledTask]
    ) -> List[Tuple[ScheduledTask, ScheduledTask]]:
        """Return pairs of scheduled tasks whose time windows overlap."""
        conflicts = []
        for i, a in enumerate(schedule):
            for b in schedule[i + 1 :]:
                a_s = datetime.strptime(a.start_time, "%H:%M")
                a_e = datetime.strptime(a.end_time, "%H:%M")
                b_s = datetime.strptime(b.start_time, "%H:%M")
                b_e = datetime.strptime(b.end_time, "%H:%M")
                if a_s < b_e and b_s < a_e:
                    conflicts.append((a, b))
        return conflicts

    def conflict_warnings(self, schedule: List[ScheduledTask]) -> List[str]:
        """Return human-readable warning strings for every detected conflict."""
        return [
            f"CONFLICT: '{a.task.title}' ({a.start_time}–{a.end_time}) "
            f"overlaps '{b.task.title}' ({b.start_time}–{b.end_time})"
            for a, b in self.detect_conflicts(schedule)
        ]

    def explain_plan(self, schedule: List[ScheduledTask]) -> str:
        """Return a plain-English summary of a generated schedule."""
        if not schedule:
            return "  No tasks could be scheduled within the available time budget."
        lines = []
        for st in schedule:
            lines.append(
                f"  {st.start_time} – {st.end_time}  "
                f"{st.task.title} ({st.task.duration_minutes} min)  "
                f"[{st.task.priority} priority]"
            )
        total = sum(s.task.duration_minutes for s in schedule)
        lines.append(f"\n  Total: {total} / {self.owner.available_minutes_per_day} min used.")
        return "\n".join(lines)
