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


# ── Scheduler tests ───────────────────────────────────────────────────────────

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


def test_generate_schedule_respects_budget():
    owner = Owner(name="Jordan", email="j@example.com", available_minutes_per_day=30)
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task("Walk",    30, "high",   "walk"))
    pet.add_task(Task("Feeding", 10, "high",   "feeding"))  # won't fit after walk
    pet.add_task(Task("Play",    20, "medium", "enrichment"))  # won't fit either

    scheduler = Scheduler(owner=owner, date="2026-06-23")
    schedule = scheduler.generate_schedule(pet)
    total = sum(s.task.duration_minutes for s in schedule)
    assert total <= owner.available_minutes_per_day


def test_detect_conflicts_finds_none_for_sequential_schedule():
    owner = Owner(name="Jordan", email="j@example.com", available_minutes_per_day=60)
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task("Walk",    20, "high", "walk"))
    pet.add_task(Task("Feeding", 10, "high", "feeding"))

    scheduler = Scheduler(owner=owner, date="2026-06-23")
    schedule = scheduler.generate_schedule(pet)
    assert scheduler.detect_conflicts(schedule) == []
