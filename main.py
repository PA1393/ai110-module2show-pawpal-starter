from pawpal_system import Owner, Pet, Task, Scheduler, ScheduledTask

SEP = "=" * 54


def section(title):
    print(f"\n{SEP}\n  {title}\n{SEP}")


def main():
    owner = Owner(
        name="Jordan",
        email="jordan@example.com",
        available_minutes_per_day=120,
    )

    # Tasks are added OUT OF ORDER on purpose to show sort_by_time working.
    mochi = Pet(name="Mochi", species="dog", age=3, breed="Shiba Inu")
    mochi.add_task(Task("Enrichment play",   20, "medium", "enrichment",  preferred_time="15:00"))
    mochi.add_task(Task("Morning walk",      30, "high",   "walk",        is_recurring=True,
                        preferred_time="07:00", due_date="2026-06-23"))
    mochi.add_task(Task("Heartworm pill",     5, "high",   "medication",  is_recurring=True,
                        recurrence_interval="weekly", preferred_time="08:00"))
    mochi.add_task(Task("Brushing",          15, "low",    "grooming",    preferred_time="17:00"))
    mochi.add_task(Task("Breakfast feeding", 10, "high",   "feeding",     is_recurring=True,
                        preferred_time="08:00", due_date="2026-06-23"))

    owner.add_pet(mochi)
    scheduler = Scheduler(owner=owner, date="2026-06-23", start_time="07:00")

    # ── 1. Generated schedule ────────────────────────────────────────────────
    section("1. Generated schedule (sort_by_time + preferred_time)")
    schedule = scheduler.generate_schedule(mochi)
    print(scheduler.explain_plan(schedule))

    # ── 2. sort_by_time ──────────────────────────────────────────────────────
    section("2. sort_by_time() — all tasks ordered by preferred slot")
    for t in scheduler.sort_by_time(mochi.get_tasks()):
        print(f"  {t.preferred_time}  {t.title:<22} [{t.priority}]")

    # ── 3. filter_tasks ──────────────────────────────────────────────────────
    section("3. filter_tasks() — incomplete only / feeding only")
    print("  Incomplete tasks:")
    for t in scheduler.filter_tasks(mochi, completed=False):
        print(f"    {t.title}")

    # Mark one complete so the filter has something to exclude
    mochi.get_tasks()[0].mark_complete()
    print(f"\n  After marking '{mochi.get_tasks()[0].title}' done:")
    print("  Remaining incomplete:")
    for t in scheduler.filter_tasks(mochi, completed=False):
        print(f"    {t.title}")

    print("\n  Feeding tasks only:")
    for t in scheduler.filter_tasks(mochi, task_type="feeding"):
        print(f"    {t.title} (completed={t.completed})")

    # ── 4. Recurring task → next occurrence ──────────────────────────────────
    section("4. Recurring tasks — mark_complete() returns next occurrence")
    walk = next(t for t in mochi.get_tasks() if t.title == "Morning walk")
    print(f"  Before: title={walk.title!r}  due={walk.due_date}  completed={walk.completed}")
    next_task = walk.mark_complete()
    print(f"  After:  completed={walk.completed}")
    if next_task:
        print(f"  Next:   title={next_task.title!r}  due={next_task.due_date}  completed={next_task.completed}")
        mochi.add_task(next_task)
        print(f"  Next task added to Mochi. Total tasks: {len(mochi.get_tasks())}")

    # ── 5. Conflict detection ────────────────────────────────────────────────
    section("5. detect_conflicts() / conflict_warnings() — overlapping tasks")
    # Manually construct an overlapping schedule to demonstrate detection
    task_a = Task("Vet appointment",  60, "high",   "appointment", preferred_time="09:00")
    task_b = Task("Grooming session", 30, "medium", "grooming",    preferred_time="09:30")
    overlapping = [
        ScheduledTask(task=task_a, start_time="09:00", end_time="10:00"),
        ScheduledTask(task=task_b, start_time="09:30", end_time="10:00"),  # starts mid-appointment
    ]
    warnings = scheduler.conflict_warnings(overlapping)
    if warnings:
        for w in warnings:
            print(f"  ⚠  {w}")
    else:
        print("  No conflicts.")

    print(f"\n  (The generated schedule above has no conflicts because")
    print(f"   generate_schedule() places tasks sequentially.)")

    print(f"\n{SEP}")


if __name__ == "__main__":
    main()
