from datetime import date, datetime, timedelta

PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}
FREQUENCIES = ("once", "daily", "weekly")
REPEAT_INTERVAL = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


class Owner:
    def __init__(self, name, available_minutes, preferences=None):
        """Create an owner with a daily time budget and no pets yet."""
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences or []
        self.pets = []

    def add_pet(self, pet):
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet):
        """Remove a pet from this owner."""
        self.pets.remove(pet)

    def get_pet(self, name):
        """Return the pet with the given name, or None if there isn't one."""
        for pet in self.pets:
            if pet.name == name:
                return pet
        return None

    def get_all_tasks(self):
        """Return every task across all pets as (pet, task) pairs."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def get_owner_info(self):
        """Return a one-line summary of the owner, their time, and their pets."""
        pet_names = ", ".join(pet.name for pet in self.pets) or "no pets"
        return f"{self.name} ({self.available_minutes} min available today) - pets: {pet_names}"


class Pet:
    def __init__(self, name, species, breed="", age=0):
        """Create a pet with its details and an empty task list."""
        self.name = name
        self.species = species
        self.breed = breed
        self.age = age
        self.tasks = []

    def add_task(self, task):
        """Add a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task):
        """Remove a care task from this pet."""
        self.tasks.remove(task)

    def get_pending_tasks(self):
        """Return this pet's tasks that are not completed yet."""
        return [task for task in self.tasks if not task.completed]

    def get_completed_tasks(self):
        """Return this pet's tasks that are already completed."""
        return [task for task in self.tasks if task.completed]

    def get_pet_info(self):
        """Return a one-line summary of the pet's details."""
        breed = f" {self.breed}" if self.breed else ""
        return f"{self.name} ({self.age}-year-old{breed} {self.species})"


class Task:
    def __init__(self, description, duration_minutes, priority="medium",
                 time=None, frequency="once", completed=False, due_date=None):
        """Create a care task and check that its fields are valid."""
        self.description = description
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.time = time  # preferred start time as "HH:MM", or None if flexible
        self.frequency = frequency
        self.completed = completed
        self.due_date = due_date or date.today()
        self._validate()

    def _validate(self):
        """Raise ValueError if priority, frequency, duration, or time is invalid."""
        if self.priority not in PRIORITY_RANK:
            raise ValueError(f"priority must be one of {list(PRIORITY_RANK)}, got {self.priority!r}")
        if self.frequency not in FREQUENCIES:
            raise ValueError(f"frequency must be one of {list(FREQUENCIES)}, got {self.frequency!r}")
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        if self.time is not None:
            # raises ValueError if not HH:MM; zero-pads so "8:00" becomes "08:00" and sorts correctly
            self.time = datetime.strptime(self.time, "%H:%M").strftime("%H:%M")

    def priority_rank(self):
        """Return the priority as a number so tasks sort correctly (high = 3)."""
        return PRIORITY_RANK[self.priority]

    def mark_complete(self):
        """Mark this task as done."""
        self.completed = True

    def mark_incomplete(self):
        """Mark this task as not done."""
        self.completed = False

    def next_occurrence(self):
        """Return a new, not-completed copy due one interval later, or None if the task doesn't repeat."""
        if self.frequency not in REPEAT_INTERVAL:
            return None
        return Task(
            self.description,
            self.duration_minutes,
            self.priority,
            time=self.time,
            frequency=self.frequency,
            due_date=self.due_date + REPEAT_INTERVAL[self.frequency],
        )

    def edit(self, description=None, duration_minutes=None, priority=None,
             time=None, frequency=None):
        """Update only the fields that are passed in."""
        if description is not None:
            self.description = description
        if duration_minutes is not None:
            self.duration_minutes = duration_minutes
        if priority is not None:
            self.priority = priority
        if time is not None:
            self.time = time
        if frequency is not None:
            self.frequency = frequency
        self._validate()

    def __str__(self):
        """Return the task as a readable line, e.g. '08:00 - Walk (30 min) [priority: high]'."""
        when = self.time or "anytime"
        return f"{when} - {self.description} ({self.duration_minutes} min) [priority: {self.priority}]"


class Scheduler:
    def __init__(self, owner):
        """Create a scheduler that plans tasks for all of the owner's pets."""
        self.owner = owner
        self.plan = []
        self.skipped = []
        self.conflicts = []

    def get_all_tasks(self, include_completed=False):
        """Retrieve tasks from every pet through the owner."""
        if include_completed:
            return self.owner.get_all_tasks()
        return self.filter_by_status(completed=False)

    def filter_by_status(self, completed):
        """Return (pet, task) pairs whose completion status matches completed (True or False)."""
        return [(pet, task) for pet, task in self.owner.get_all_tasks() if task.completed == completed]

    def enter_task(self, pet, task):
        """Add a task to one of the owner's pets, rejecting pets that aren't theirs."""
        if pet not in self.owner.pets:
            raise ValueError(f"{pet.name} does not belong to {self.owner.name}")
        pet.add_task(task)

    def mark_task_complete(self, task):
        """Mark a task done and, if it repeats, add its next occurrence to the same pet."""
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            for pet in self.owner.pets:
                if task in pet.tasks:
                    pet.add_task(next_task)
                    break
        return next_task

    def get_tasks_due(self, day=None):
        """Return pending (pet, task) pairs due on or before day (default today), so overdue tasks are kept."""
        day = day or date.today()
        return [(pet, task) for pet, task in self.get_all_tasks() if task.due_date <= day]

    def edit_task(self, task, **changes):
        """Apply the given field changes to a task."""
        task.edit(**changes)

    def sort_by_priority(self, pairs):
        """Sort highest priority first; ties go to the shorter task."""
        return sorted(pairs, key=lambda pt: (-pt[1].priority_rank(), pt[1].duration_minutes))

    def sort_by_time(self, pairs):
        """Sort earliest preferred time first; flexible tasks go last."""
        return sorted(pairs, key=lambda pt: (pt[1].time is None, pt[1].time or ""))

    def detect_conflicts(self, pairs=None):
        """Return warning messages for pending tasks that share the same date and start time."""
        if pairs is None:
            pairs = self.get_all_tasks()

        slots = {}
        for pet, task in pairs:
            if task.time is None:
                continue  # "anytime" tasks can't clash
            slots.setdefault((task.due_date, task.time), []).append((pet, task))

        warnings = []
        for (day, time), group in sorted(slots.items()):
            if len(group) > 1:
                names = " and ".join(f"'{task.description}' ({pet.name})" for pet, task in group)
                pets = {pet.name for pet, _ in group}
                who = f"{group[0][0].name} has" if len(pets) == 1 else "you have"
                warnings.append(f"Conflict on {day} at {time}: {who} {names} scheduled at the same time.")
        return warnings

    def generate_plan(self, day=None):
        """Choose tasks due by day (default today) by priority until time runs out, then order by time."""
        self.plan = []
        self.skipped = []
        minutes_left = self.owner.available_minutes

        for pet, task in self.sort_by_priority(self.get_tasks_due(day)):
            if task.duration_minutes <= minutes_left:
                self.plan.append((pet, task))
                minutes_left -= task.duration_minutes
            else:
                self.skipped.append((pet, task))

        self.plan = self.sort_by_time(self.plan)
        self.conflicts = self.detect_conflicts(self.plan)
        return self.plan

    def explain_plan(self):
        """Return a text explanation of the plan and why any tasks were skipped."""
        if not self.plan and not self.skipped:
            return "No plan yet. Call generate_plan() first, or add some tasks."

        used = sum(task.duration_minutes for _, task in self.plan)
        lines = [f"Plan for {self.owner.name}: {used} of {self.owner.available_minutes} minutes used."]
        for pet, task in self.plan:
            lines.append(f"  {task} for {pet.name}")
        if self.skipped:
            lines.append("Skipped (not enough time left after higher-priority tasks):")
            for pet, task in self.skipped:
                lines.append(f"  {task.description} for {pet.name} ({task.duration_minutes} min, {task.priority})")
        for warning in self.conflicts:
            lines.append(f"WARNING: {warning}")
        lines.append("Tasks were chosen highest priority first, then ordered by time of day.")
        return "\n".join(lines)
