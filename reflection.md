# PawPal+ Project Reflection

## 1. System Design

**Three core actions a user should be able to perform:**

1. **Add a pet** — register a pet (name, species, age, breed) under their owner profile so the system knows who it's planning for.
2. **Add care tasks to a pet** — attach tasks (walks, feedings, medications, appointments) with a duration, priority, and recurrence so the scheduler has something to work with.
3. **Generate and view a daily schedule** — produce a prioritized, conflict-free time-blocked plan for the day and read a plain-English explanation of why each task was included.

**a. Initial design**

The system is built around five classes:

- **Task** — a dataclass holding everything about a single care activity: title, duration in minutes, priority level (high/medium/low), task type (walk, feeding, medication, etc.), and whether it recurs (daily, weekly, as-needed). It is a pure data object with no knowledge of pets or schedules.
- **Pet** — a dataclass representing one animal. It owns a list of Tasks and exposes methods to add, remove, and retrieve them. It is the unit the Scheduler operates on.
- **Owner** — a dataclass representing the human. It holds a list of Pets and a daily availability budget (minutes). The Scheduler reads this budget to know how much can be packed into a day.
- **ScheduledTask** — a dataclass that wraps a Task once it has been assigned a concrete start/end time and a human-readable reason string. The Scheduler produces these; the UI and demo script consume them.
- **Scheduler** — the only non-dataclass. It receives an Owner and a date, then provides four operations: sort tasks by priority, generate a time-blocked schedule that respects the owner's availability, detect overlapping time slots, and produce a plain-English explanation of the final plan.

**b. Design changes**

During Phase 4 (algorithmic layer), two fields were added to `Task`: `preferred_time` (HH:MM string for when in the day a task is preferred) and `due_date` (YYYY-MM-DD, empty = any day). These weren't in the original UML because the initial design treated scheduling as purely priority-driven. Once recurring tasks required a concrete next-due date, and the UI needed time-of-day hints for a realistic schedule, both fields became necessary. The `mark_complete()` signature also changed from `None` to `Optional[Task]` to support returning a ready-made next-occurrence object for recurring tasks.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints: (1) the owner's daily time budget (`available_minutes_per_day`), which hard-caps how much can fit in a day; (2) each task's `preferred_time`, which is the primary sort key — tasks are grouped by when they should happen rather than just by importance; (3) task `priority` (high/medium/low), used as a tiebreaker when two tasks share the same preferred slot. `preferred_time` was made the primary constraint because pet care routines are inherently time-driven: a morning walk belongs in the morning whether it is high or low priority. Priority then breaks ties within the same time window to ensure the more important task runs first when they compete for the same slot.

**b. Tradeoffs**

The scheduler uses a greedy algorithm: tasks are sorted by preferred_time and placed as early as possible after their preferred slot, with the time pointer advancing after each placement. This means it cannot backtrack — if a 60-minute vet appointment claims 09:00–10:00, a 5-minute feeding preferred at 09:30 gets pushed to 10:00 instead of being inserted before the appointment. This is a greedy-vs-optimal tradeoff. It is reasonable for a single-day pet care schedule because predictability and simplicity matter more than mathematical optimality: an owner can read and trust a sequential plan, and pet care tasks are not so tightly constrained that the global optimum would look meaningfully different from the greedy result.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
