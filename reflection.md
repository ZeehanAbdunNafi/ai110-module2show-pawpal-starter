# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The system supports three core user actions:

1. The user can enter basic information about themselves and their pet, such as name and species, to personalize the planning system.

2. The user can add and manage pet care tasks, including details like task type, duration, and priority.

3. The user can generate a daily schedule that organizes tasks based on constraints such as time availability and priority, and the system explains why tasks were selected and ordered.

Based on these actions, I designed the system using the following classes:

- Owner: stores user information and preferences; can set available time and view the daily plan
- OwnerPreferences: captures scheduling constraints (earliest start, latest end, max tasks, category preferences)
- Pet: stores pet details and associated tasks; supports task linking and detail updates
- PetCareTask: represents individual care tasks with duration, priority, status, type, and recurring flag
- Scheduler: sorts/filter tasks, generates a daily schedule, and records explanations
- DayPlan: stores scheduled entries, total planned time, and explanation notes

I also asked Copilot to review my skeleton in `#file:pawpal_system.py` and requested feedback on missing relationships or potential logic bottlenecks. Copilot confirmed the core associations are right (Owner->Pet, Pet->Task, Scheduler->Task->DayPlan) and suggested ensuring tasks can reference their related pet or owner if needed in future extensions.

**b. Design changes**

The design changed during implementation. Initially, I planned to use a simple Task class, but I changed it to PetCareTask with more structured attributes like category and priority using enums. I also introduced OwnerPreferences as a separate class to better organize scheduling constraints. This made the system more modular and easier to manage.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers several constraints:

- Available time (earliest start and latest end)
- Task priority (low, medium, high)
- Maximum number of tasks
- Preferred and avoided task categories
- Task duration

Priority was the most important factor, followed by time constraints. High-priority tasks are scheduled first, and tasks must fit within the available time window.

**b. Tradeoffs**

One tradeoff is that tasks outside preferred categories may be skipped even if time is available. This simplifies decision-making but may ignore some valid tasks. This is reasonable because the goal is to respect user preferences while still prioritizing important tasks.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI to help brainstorm the system design, generate UML diagrams, and guide the implementation of scheduling logic. I also used it to refine class structures and debug issues.

**b. Judgment and verification**

At one point, AI suggested adding more complex relationships and extra classes. I chose not to include them because they were unnecessary for this project. I verified decisions by comparing them with the project requirements and ensuring the system remained simple and functional.

---

## 4. Testing and Verification

**a. What you tested**

I tested the following behaviors:

- Tasks being sorted by priority
- Tasks being scheduled within time constraints
- Tasks being skipped when constraints are not met
- Explanation messages being generated correctly

These tests were important to ensure the scheduler works logically and produces meaningful output.

**b. Confidence**

I am confident that the scheduler works correctly for normal cases. If I had more time, I would test edge cases such as overlapping constraints, very tight schedules, and large numbers of tasks.

---

## 5. Reflection

**a. What went well**

The scheduling logic and explanation system worked well. The system successfully generates a clear and understandable daily plan.

**b. What you would improve**

I would improve the UI and make the scheduler more flexible, such as allowing partial scheduling instead of skipping tasks entirely.

**c. Key takeaway**

One important takeaway is that designing a system before coding makes implementation much easier. Breaking the problem into classes helped create a clean and organized solution.