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

Run `python main.py` to see the full algorithmic feature demo:

```
======================================================
  1. Generated schedule (sort_by_time + preferred_time)
======================================================
  07:00 – 07:30  Morning walk (30 min)  [high priority]
  08:00 – 08:05  Heartworm pill (5 min)  [high priority]
  08:05 – 08:15  Breakfast feeding (10 min)  [high priority]
  15:00 – 15:20  Enrichment play (20 min)  [medium priority]
  17:00 – 17:15  Brushing (15 min)  [low priority]

  Total: 80 / 120 min used.

======================================================
  2. sort_by_time() — all tasks ordered by preferred slot
======================================================
  07:00  Morning walk           [high]
  08:00  Heartworm pill         [high]
  08:00  Breakfast feeding      [high]
  15:00  Enrichment play        [medium]
  17:00  Brushing               [low]

======================================================
  3. filter_tasks() — incomplete only / feeding only
======================================================
  ...

======================================================
  4. Recurring tasks — mark_complete() returns next occurrence
======================================================
  Before: title='Morning walk'  due=2026-06-23  completed=False
  After:  completed=True
  Next:   title='Morning walk'  due=2026-06-24  completed=False

======================================================
  5. detect_conflicts() / conflict_warnings() — overlapping tasks
======================================================
  ⚠  CONFLICT: 'Vet appointment' (09:00–10:00) overlaps 'Grooming session' (09:30–10:00)
```

## 🧪 Testing PawPal+

```bash
# Activate the virtual environment first:
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Run the full test suite:
python -m pytest tests/ -v
```

### What the tests cover

| Group | Tests | What's verified |
|-------|-------|-----------------|
| Task lifecycle | 6 | `mark_complete()` sets status; recurring tasks return a next-occurrence `Task`; non-recurring and `as_needed` return `None`; idempotent completion |
| Pet CRUD | 2 | Adding a task increases count; removing a task by title decreases count |
| Owner CRUD | 2 | Adding / removing pets by name |
| Sorting | 2 | Priority sort (high→low) and time sort (HH:MM ascending, priority tiebreaker) |
| Filtering | 2 | Filter by `completed` status; filter by `task_type`; empty-result case |
| Schedule generation | 3 | Respects daily budget; honors `preferred_time`; handles pet with no tasks; exact-budget fit |
| Conflict detection | 4 | No conflicts on sequential schedule; overlap detected; exact same start time flagged; `conflict_warnings` returns strings |
| Edge cases | 3 | Empty schedule message; all attributes preserved on next occurrence; no-match filter |

### Sample test run

```
platform linux -- Python 3.12.3, pytest-9.1.1
collected 26 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  3%]
tests/test_pawpal.py::test_mark_complete_is_idempotent PASSED            [  7%]
tests/test_pawpal.py::test_mark_complete_returns_none_for_non_recurring PASSED [ 11%]
tests/test_pawpal.py::test_mark_complete_returns_next_task_for_daily_recurring PASSED [ 15%]
tests/test_pawpal.py::test_mark_complete_returns_next_task_for_weekly_recurring PASSED [ 19%]
tests/test_pawpal.py::test_mark_complete_as_needed_returns_none PASSED   [ 23%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [ 26%]
tests/test_pawpal.py::test_remove_task_decreases_pet_task_count PASSED   [ 30%]
tests/test_pawpal.py::test_add_pet_increases_owner_pet_count PASSED      [ 34%]
tests/test_pawpal.py::test_remove_pet_decreases_owner_pet_count PASSED   [ 38%]
tests/test_pawpal.py::test_sort_tasks_high_before_low PASSED             [ 42%]
tests/test_pawpal.py::test_sort_by_time_orders_by_preferred_time PASSED  [ 46%]
tests/test_pawpal.py::test_filter_tasks_by_completion_status PASSED      [ 50%]
tests/test_pawpal.py::test_filter_tasks_by_type PASSED                   [ 53%]
tests/test_pawpal.py::test_generate_schedule_respects_budget PASSED      [ 57%]
tests/test_pawpal.py::test_generate_schedule_honors_preferred_time PASSED [ 61%]
tests/test_pawpal.py::test_detect_conflicts_finds_none_for_sequential_schedule PASSED [ 65%]
tests/test_pawpal.py::test_detect_conflicts_finds_overlap PASSED         [ 69%]
tests/test_pawpal.py::test_conflict_warnings_returns_strings PASSED      [ 73%]
tests/test_pawpal.py::test_generate_schedule_pet_with_no_tasks PASSED    [ 76%]
tests/test_pawpal.py::test_generate_schedule_exact_budget_fit PASSED     [ 80%]
tests/test_pawpal.py::test_sort_by_time_priority_tiebreaker PASSED       [ 84%]
tests/test_pawpal.py::test_detect_conflicts_exact_same_start_time PASSED [ 88%]
tests/test_pawpal.py::test_filter_tasks_no_matches_returns_empty PASSED  [ 92%]
tests/test_pawpal.py::test_explain_plan_empty_schedule_message PASSED    [ 96%]
tests/test_pawpal.py::test_next_occurrence_preserves_all_attributes PASSED [100%]

26 passed in 0.04s
```

### Confidence level: ★★★★☆ (4/5)

The core scheduling logic — sorting, filtering, budget enforcement, conflict detection, and recurring tasks — is thoroughly covered by tests across both happy paths and edge cases. The main gap is integration-level testing: the tests verify individual methods in isolation but don't test the full flow from UI input through session state to schedule output. A full end-to-end Streamlit test would push this to 5/5.

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sort by priority | `Scheduler.sort_tasks()` | Priority descending (high→low); ties broken by duration ascending (shorter first) |
| Sort by time | `Scheduler.sort_by_time()` | Sorts by `Task.preferred_time` (HH:MM) ascending; within the same slot, priority descending |
| Filter by status / type | `Scheduler.filter_tasks()` | Keyword args: `completed=True/False`, `task_type="walk"` etc. |
| Schedule generation | `Scheduler.generate_schedule()` | Greedy; respects preferred_time and owner's daily budget; skips tasks that won't fit |
| Conflict detection | `Scheduler.detect_conflicts()` | O(n²) pairwise window-overlap check on a list of ScheduledTasks |
| Conflict warnings | `Scheduler.conflict_warnings()` | Wraps `detect_conflicts()` and returns human-readable warning strings |
| Recurring tasks | `Task.mark_complete()` | Returns a new `Task` for the next occurrence (daily +1 day, weekly +7 days); `None` for non-recurring |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
