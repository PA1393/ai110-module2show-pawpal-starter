import pytest
from pawpal_system import Task, Pet, Owner, Scheduler, ScheduledTask


# ── Task tests ────────────────────────────────────────────────────────────────

def test_mark_complete_changes_status():
    task = Task("Morning walk", 30, "high", "walk")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_mark_complete_is_idempotent():
    task = Task("Feeding", 10, "high", "feeding")
    task.mark_complete()
    task.mark_complete()
    assert task.completed is True


def test_mark_complete_returns_none_for_non_recurring():
    task = Task("One-off grooming", 30, "low", "grooming", is_recurring=False)
    result = task.mark_complete()
    assert result is None


def test_mark_complete_returns_next_task_for_daily_recurring():
    task = Task(
        "Morning walk", 30, "high", "walk",
        is_recurring=True, recurrence_interval="daily", due_date="2026-06-23",
    )
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == "2026-06-24"
    assert next_task.completed is False
    assert next_task.title == "Morning walk"


def test_mark_complete_returns_next_task_for_weekly_recurring():
    task = Task(
        "Heartworm pill", 5, "high", "medication",
        is_recurring=True, recurrence_interval="weekly", due_date="2026-06-23",
    )
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == "2026-06-30"


def test_mark_complete_as_needed_returns_none():
    task = Task(
        "Extra brushing", 15, "low", "grooming",
        is_recurring=True, recurrence_interval="as_needed",
    )
    result = task.mark_complete()
    assert result is None


# ── Pet tests ─────────────────────────────────────────────────────────────────

def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("Morning walk", 30, "high", "walk"))
    assert len(pet.get_tasks()) == 1
    pet.add_task(Task("Feeding", 10, "high", "feeding"))
    assert len(pet.get_tasks()) == 2


def test_remove_task_decreases_pet_task_count():
    pet = Pet(name="Luna", species="cat", age=5)
    pet.add_task(Task("Feeding", 5, "high", "feeding"))
    pet.add_task(Task("Play", 10, "medium", "enrichment"))
    pet.remove_task("Feeding")
    assert len(pet.get_tasks()) == 1
    assert pet.get_tasks()[0].title == "Play"


# ── Owner tests ───────────────────────────────────────────────────────────────

def test_add_pet_increases_owner_pet_count():
    owner = Owner(name="Jordan", email="jordan@example.com")
    assert len(owner.get_pets()) == 0
    owner.add_pet(Pet(name="Mochi", species="dog", age=3))
    assert len(owner.get_pets()) == 1


def test_remove_pet_decreases_owner_pet_count():
    owner = Owner(name="Jordan", email="jordan@example.com")
    owner.add_pet(Pet(name="Mochi", species="dog", age=3))
    owner.add_pet(Pet(name="Luna", species="cat", age=5))
    owner.remove_pet("Mochi")
    assert len(owner.get_pets()) == 1
    assert owner.get_pets()[0].name == "Luna"


# ── Scheduler: sorting ────────────────────────────────────────────────────────

def test_sort_tasks_high_before_low():
    owner = Owner(name="Jordan", email="j@example.com")
    scheduler = Scheduler(owner=owner, date="2026-06-23")
    tasks = [
        Task("Low task",    5, "low",    "grooming"),
        Task("High task",   5, "high",   "walk"),
        Task("Medium task", 5, "medium", "enrichment"),
    ]
    sorted_tasks = scheduler.sort_tasks(tasks)
    assert sorted_tasks[0].priority == "high"
    assert sorted_tasks[1].priority == "medium"
    assert sorted_tasks[2].priority == "low"


def test_sort_by_time_orders_by_preferred_time():
    owner = Owner(name="Jordan", email="j@example.com")
    scheduler = Scheduler(owner=owner, date="2026-06-23")
    tasks = [
        Task("Evening walk",   20, "high", "walk",    preferred_time="17:00"),
        Task("Morning feed",   10, "high", "feeding", preferred_time="07:00"),
        Task("Afternoon play", 15, "low",  "enrichment", preferred_time="13:00"),
    ]
    result = scheduler.sort_by_time(tasks)
    assert result[0].preferred_time == "07:00"
    assert result[1].preferred_time == "13:00"
    assert result[2].preferred_time == "17:00"


# ── Scheduler: filtering ──────────────────────────────────────────────────────

def test_filter_tasks_by_completion_status():
    owner = Owner(name="Jordan", email="j@example.com")
    scheduler = Scheduler(owner=owner, date="2026-06-23")
    pet = Pet(name="Mochi", species="dog", age=3)
    done = Task("Walk", 30, "high", "walk")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(Task("Feeding", 10, "high", "feeding"))

    incomplete = scheduler.filter_tasks(pet, completed=False)
    complete = scheduler.filter_tasks(pet, completed=True)
    assert len(incomplete) == 1
    assert len(complete) == 1
    assert incomplete[0].title == "Feeding"


def test_filter_tasks_by_type():
    owner = Owner(name="Jordan", email="j@example.com")
    scheduler = Scheduler(owner=owner, date="2026-06-23")
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task("Walk",    30, "high",   "walk"))
    pet.add_task(Task("Feeding", 10, "high",   "feeding"))
    pet.add_task(Task("Play",    15, "medium", "enrichment"))

    walks = scheduler.filter_tasks(pet, task_type="walk")
    assert len(walks) == 1
    assert walks[0].title == "Walk"


# ── Scheduler: schedule generation ───────────────────────────────────────────

def test_generate_schedule_respects_budget():
    owner = Owner(name="Jordan", email="j@example.com", available_minutes_per_day=30)
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task("Walk",    30, "high",   "walk",        preferred_time="08:00"))
    pet.add_task(Task("Feeding", 10, "high",   "feeding",     preferred_time="08:30"))
    pet.add_task(Task("Play",    20, "medium", "enrichment",  preferred_time="09:00"))

    scheduler = Scheduler(owner=owner, date="2026-06-23")
    schedule = scheduler.generate_schedule(pet)
    total = sum(s.task.duration_minutes for s in schedule)
    assert total <= owner.available_minutes_per_day


def test_generate_schedule_honors_preferred_time():
    owner = Owner(name="Jordan", email="j@example.com", available_minutes_per_day=120)
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task("Evening walk", 30, "high", "walk", preferred_time="17:00"))

    scheduler = Scheduler(owner=owner, date="2026-06-23", start_time="08:00")
    schedule = scheduler.generate_schedule(pet)
    assert len(schedule) == 1
    assert schedule[0].start_time == "17:00"   # respects preferred_time, not just start_time


# ── Scheduler: conflict detection ────────────────────────────────────────────

def test_detect_conflicts_finds_none_for_sequential_schedule():
    owner = Owner(name="Jordan", email="j@example.com", available_minutes_per_day=60)
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task("Walk",    20, "high", "walk",    preferred_time="08:00"))
    pet.add_task(Task("Feeding", 10, "high", "feeding", preferred_time="09:00"))

    scheduler = Scheduler(owner=owner, date="2026-06-23")
    schedule = scheduler.generate_schedule(pet)
    assert scheduler.detect_conflicts(schedule) == []


def test_detect_conflicts_finds_overlap():
    owner = Owner(name="Jordan", email="j@example.com", available_minutes_per_day=120)
    scheduler = Scheduler(owner=owner, date="2026-06-23")
    task_a = Task("Vet", 60, "high", "appointment")
    task_b = Task("Groom", 30, "medium", "grooming")
    overlapping = [
        ScheduledTask(task=task_a, start_time="09:00", end_time="10:00"),
        ScheduledTask(task=task_b, start_time="09:30", end_time="10:00"),
    ]
    conflicts = scheduler.detect_conflicts(overlapping)
    assert len(conflicts) == 1


def test_conflict_warnings_returns_strings():
    owner = Owner(name="Jordan", email="j@example.com", available_minutes_per_day=120)
    scheduler = Scheduler(owner=owner, date="2026-06-23")
    task_a = Task("Vet",   60, "high",   "appointment")
    task_b = Task("Groom", 30, "medium", "grooming")
    overlapping = [
        ScheduledTask(task=task_a, start_time="09:00", end_time="10:00"),
        ScheduledTask(task=task_b, start_time="09:30", end_time="10:00"),
    ]
    warnings = scheduler.conflict_warnings(overlapping)
    assert len(warnings) == 1
    assert "CONFLICT" in warnings[0]
    assert "Vet" in warnings[0]
