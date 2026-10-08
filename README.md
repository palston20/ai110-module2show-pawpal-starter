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

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:


==================================================
                 Today's Schedule                 
==================================================
Jordan (90 min available today) - pets: Biscuit, Mochi
--------------------------------------------------
  07:30  Breakfast          Mochi     10 min  [high]
  08:00  Morning walk       Biscuit   30 min  [high]
  16:00  Fetch in the yard  Biscuit   20 min  [low]
  18:00  Brushing           Mochi     15 min  [medium]
--------------------------------------------------
Total: 75 of 90 minutes


## 🧪 Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

### What the tests cover

The 22 tests in `tests/test_pawpawl.py` cover the scheduler's core behavior:

- **Sorting:** plans come back in chronological order regardless of priority or the order tasks were added. Single-digit hours (`"8:00"`), midnight edge times and multiple "anytime" tasks are all handled. Priority ties go to the shorter task.
- **Recurring tasks:** completing a daily task creates a copy due tomorrow (including year rollover), and completing a weekly task creates one due next week. `once` tasks don't repeat. The new copy keeps the task's details, belongs to the same pet and only shows up in the plan for its due date.
- **Conflict detection:** tasks with the same date and start time are flagged, for one pet or across pets. Three clashing tasks produce one warning. "Anytime", completed, skipped and different-day tasks are not flagged. Warnings appear in `explain_plan()`.
- **Basics:** marking tasks complete, adding tasks to pets, and filtering by completed or pending status.

### Sample test output

```
============================= test session starts ==============================
platform darwin -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/parisalston/Desktop/python folder/ai-projects/ai110-module2show-pawpal-starter
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collected 22 items

tests/test_pawpawl.py ......................                             [100%]

============================== 22 passed in 0.02s ==============================
```

### Confidence level: ⭐⭐⭐⭐☆ (4/5)

All 22 tests pass, and they cover the main scheduling paths: sorting, recurring tasks, conflict detection and the time budget. It's not 5 stars because of a few known gaps:

- Conflict detection only catches identical start times, not overlapping durations.
- Completing the same recurring task twice creates a duplicate next occurrence.
- A failed `edit()` leaves the invalid value on the task.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_priority`, `Scheduler.sort_by_time` | Tasks are picked highest priority first, and shorter tasks win ties. The final plan is then reordered by preferred start time ("HH:MM"), with "anytime" tasks last. Times are zero-padded on input, so `"8:00"` sorts correctly. |
| Filtering | `Scheduler.generate_plan`, `Scheduler.get_tasks_due`, `Scheduler.filter_by_status` | Only pending tasks due today or earlier are considered, so overdue tasks carry over. Tasks are added until the owner's `available_minutes` runs out, and anything that doesn't fit goes into `scheduler.skipped`. `filter_by_status(True/False)` returns completed or pending tasks. |
| Conflict handling | `Scheduler.detect_conflicts` | Flags tasks with the same due date and the same start time, for one pet or across pets. Runs automatically after `generate_plan` and appears as warnings in `explain_plan`. Limitation: it only catches identical start times, not overlapping durations (e.g., a 30-min task at 08:00 and another at 08:15). |
| Recurring tasks | `Task.next_occurrence`, `Scheduler.mark_task_complete` | Completing a `daily` or `weekly` task automatically adds a fresh copy to the same pet, due 1 day or 1 week later. `once` tasks don't repeat. |


## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
