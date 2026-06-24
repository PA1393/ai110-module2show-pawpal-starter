# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Run `python main.py` to see the CLI demo:

```
====================================================
  PawPal+ Daily Schedule
  Owner : Jordan  (jordan@example.com)
  Budget: 90 min available today
====================================================

--- Mochi (Shiba Inu, age 3) ---
  08:00 – 08:05  Heartworm pill (5 min)  [high priority]
  08:05 – 08:15  Breakfast feeding (10 min)  [high priority]
  08:15 – 08:45  Morning walk (30 min)  [high priority]
  08:45 – 09:05  Enrichment play (20 min)  [medium priority]
  09:05 – 09:20  Brushing (15 min)  [low priority]

  Total: 80 / 90 min used.
  No scheduling conflicts.

--- Luna (Tabby, age 5) ---
  08:00 – 08:05  Breakfast feeding (5 min)  [high priority]
  08:05 – 09:05  Vet appointment (60 min)  [high priority]
  09:05 – 09:15  Laser pointer play (10 min)  [medium priority]

  Total: 75 / 90 min used.
  No scheduling conflicts.

====================================================
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
platform linux -- Python 3.12.3, pytest-9.1.1
collected 9 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [ 11%]
tests/test_pawpal.py::test_mark_complete_is_idempotent PASSED            [ 22%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [ 33%]
tests/test_pawpal.py::test_remove_task_decreases_pet_task_count PASSED   [ 44%]
tests/test_pawpal.py::test_add_pet_increases_owner_pet_count PASSED      [ 55%]
tests/test_pawpal.py::test_remove_pet_decreases_owner_pet_count PASSED   [ 66%]
tests/test_pawpal.py::test_sort_tasks_high_before_low PASSED             [ 77%]
tests/test_pawpal.py::test_generate_schedule_respects_budget PASSED      [ 88%]
tests/test_pawpal.py::test_detect_conflicts_finds_none_for_sequential_schedule PASSED [100%]

9 passed in 0.02s
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_tasks()` | Priority descending (high→low); ties broken by duration ascending |
| Filtering | `Scheduler.generate_schedule()` | Skips tasks that exceed remaining daily budget; continues checking smaller ones |
| Conflict handling | `Scheduler.detect_conflicts()` | Compares every pair of ScheduledTask windows for overlap |
| Recurring tasks | `Task.is_recurring`, `Task.recurrence_interval` | Fields stored on Task; "daily" / "weekly" / "as_needed" |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
