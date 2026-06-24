from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    owner = Owner(
        name="Jordan",
        email="jordan@example.com",
        available_minutes_per_day=90,
    )

    mochi = Pet(name="Mochi", species="dog", age=3, breed="Shiba Inu")
    mochi.add_task(Task("Morning walk",       30, "high",   "walk",        is_recurring=True))
    mochi.add_task(Task("Breakfast feeding",  10, "high",   "feeding",     is_recurring=True))
    mochi.add_task(Task("Heartworm pill",      5, "high",   "medication",  is_recurring=True, recurrence_interval="weekly"))
    mochi.add_task(Task("Enrichment play",    20, "medium", "enrichment"))
    mochi.add_task(Task("Brushing",           15, "low",    "grooming"))

    luna = Pet(name="Luna", species="cat", age=5, breed="Tabby")
    luna.add_task(Task("Breakfast feeding",   5,  "high",   "feeding",     is_recurring=True))
    luna.add_task(Task("Vet appointment",     60, "high",   "appointment"))
    luna.add_task(Task("Laser pointer play",  10, "medium", "enrichment"))

    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner=owner, date="2026-06-23", start_time="08:00")

    print("=" * 52)
    print(f"  PawPal+ Daily Schedule")
    print(f"  Owner : {owner.name}  ({owner.email})")
    print(f"  Budget: {owner.available_minutes_per_day} min available today")
    print("=" * 52)

    for pet in owner.get_pets():
        schedule = scheduler.generate_schedule(pet)
        print(f"\n--- {pet.name} ({pet.breed}, age {pet.age}) ---")
        print(scheduler.explain_plan(schedule))

        conflicts = scheduler.detect_conflicts(schedule)
        if conflicts:
            print("  ⚠  Conflicts detected:")
            for a, b in conflicts:
                print(f"     {a.task.title} overlaps {b.task.title}")
        else:
            print("  No scheduling conflicts.")

    print("\n" + "=" * 52)


if __name__ == "__main__":
    main()
