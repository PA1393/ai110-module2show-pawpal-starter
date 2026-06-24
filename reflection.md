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

No changes yet — this section will be updated after Phase 2 implementation if the skeleton needs to evolve.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
