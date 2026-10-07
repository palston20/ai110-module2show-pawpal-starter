from datetime import datetime

PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}
FREQUENCIES = ("once", "daily", "weekly")


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

    def get_pet_info(self):
        """Return a one-line summary of the pet's details."""
        breed = f" {self.breed}" if self.breed else ""
        return f"{self.name} ({self.age}-year-old{breed} {self.species})"


class Task:
    def __init__(self, description, duration_minutes, priority="medium",
                 time=None, frequency="once", completed=False):
        """Create a care task and check that its fields are valid."""
        self.description = description
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.time = time  # preferred start time as "HH:MM", or None if flexible
        self.frequency = frequency
        self.completed = completed
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
            datetime.strptime(self.time, "%H:%M")  # raises ValueError if not HH:MM

    def priority_rank(self):
        """Return the priority as a number so tasks sort correctly (high = 3)."""
        return PRIORITY_RANK[self.priority]

    def mark_complete(self):
        """Mark this task as done."""
        self.completed = True

    def mark_incomplete(self):
        """Mark this task as not done."""
        self.completed = False

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

    def get_all_tasks(self, include_completed=False):
        """Retrieve tasks from every pet through the owner."""
        pairs = self.owner.get_all_tasks()
        if include_completed:
            return pairs
        return [(pet, task) for pet, task in pairs if not task.completed]

    def enter_task(self, pet, task):
        """Add a task to one of the owner's pets, rejecting pets that aren't theirs."""
        if pet not in self.owner.pets:
            raise ValueError(f"{pet.name} does not belong to {self.owner.name}")
        pet.add_task(task)

    def edit_task(self, task, **changes):
        """Apply the given field changes to a task."""
        task.edit(**changes)

    def sort_by_priority(self, pairs):
        """Sort highest priority first; ties go to the shorter task."""
        return sorted(pairs, key=lambda pt: (-pt[1].priority_rank(), pt[1].duration_minutes))

    def sort_by_time(self, pairs):
        """Sort earliest preferred time first; flexible tasks go last."""
        return sorted(pairs, key=lambda pt: (pt[1].time is None, pt[1].time or ""))

    def generate_plan(self):
        """Choose tasks by priority until time runs out, then order them by time of day."""
        self.plan = []
        self.skipped = []
        minutes_left = self.owner.available_minutes

        for pet, task in self.sort_by_priority(self.get_all_tasks()):
            if task.duration_minutes <= minutes_left:
                self.plan.append((pet, task))
                minutes_left -= task.duration_minutes
            else:
                self.skipped.append((pet, task))

        self.plan = self.sort_by_time(self.plan)
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
        lines.append("Tasks were chosen highest priority first, then ordered by time of day.")
        return "\n".join(lines)
