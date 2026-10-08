from pawpal_system import Task
from pawpal_system import Pet
from pawpal_system import Owner
from pawpal_system import Scheduler


def print_todays_schedule(scheduler):
    """Generate today's plan and print it with totals, skipped tasks, and conflict warnings."""
    plan = scheduler.generate_plan()
    owner = scheduler.owner
    used = sum(task.duration_minutes for _, task in plan)

    print("=" * 50)
    print("Today's Schedule".center(50))
    print("=" * 50)
    print(owner.get_owner_info())
    print("-" * 50)

    if not plan:
        print("No tasks scheduled for today.")
    for pet, task in plan:
        when = task.time or "Anytime"
        print(f"{when:>7}  {task.description:<18} {pet.name:<8} {task.duration_minutes:>3} min  [{task.priority}]")

    print("-" * 50)
    print(f"Total: {used} of {owner.available_minutes} minutes")

    if scheduler.skipped:
        print("\nSkipped (not enough time):")
        for pet, task in scheduler.skipped:
            print(f"  - {task.description} for {pet.name} ({task.duration_minutes} min, {task.priority})")

    for warning in scheduler.conflicts:
        print(f"\nWARNING: {warning}")


def print_tasks_as_entered(scheduler):
    """Print pending tasks in the order they were added, before any sorting."""
    print("Tasks in the order they were entered:")
    for pet, task in scheduler.get_all_tasks():
        when = task.time or "Anytime"
        print(f"  {when:>7}  {task.description} ({pet.name})")
    print()


owner = Owner("Jordan", available_minutes=120)

biscuit = Pet("Biscuit", "dog", breed="Golden Retriever", age=3)
mochi = Pet("Mochi", "cat", breed="Tabby", age=2)
owner.add_pet(biscuit)
owner.add_pet(mochi)

# Tasks are added out of time order on purpose to show that the scheduler sorts them.
scheduler = Scheduler(owner)
scheduler.enter_task(mochi, Task("Brushing", 15, "medium", time="18:00", frequency="weekly"))
scheduler.enter_task(biscuit, Task("Fetch in the yard", 20, "low", time="16:00"))
scheduler.enter_task(mochi, Task("Play with wand toy", 10, "low"))
scheduler.enter_task(biscuit, Task("Morning walk", 30, "high", time="08:00", frequency="daily"))
scheduler.enter_task(biscuit, Task("Joint meds", 5, "high", time="9:15", frequency="daily"))
breakfast = Task("Breakfast", 10, "high", time="07:30", frequency="daily")
scheduler.enter_task(mochi, breakfast)

# Same time as Biscuit's morning walk, so the scheduler should warn about it.
scheduler.enter_task(mochi, Task("Clean litter box", 5, "medium", time="08:00", frequency="daily"))

if __name__ == "__main__":
    print_tasks_as_entered(scheduler)
    print_todays_schedule(scheduler)

    # Completing a daily task automatically creates tomorrow's copy.
    next_breakfast = scheduler.mark_task_complete(breakfast)
    print(f"\nMarked '{breakfast.description}' complete for {breakfast.due_date}.")
    print(f"Next '{next_breakfast.description}' is due {next_breakfast.due_date}.")
