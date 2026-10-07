from pawpal_system import Task
from pawpal_system import Pet
from pawpal_system import Owner
from pawpal_system import Scheduler


def print_todays_schedule(scheduler):
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


owner = Owner("Jordan", available_minutes=90)

biscuit = Pet("Biscuit", "dog", breed="Golden Retriever", age=3)
mochi = Pet("Mochi", "cat", breed="Tabby", age=2)
owner.add_pet(biscuit)
owner.add_pet(mochi)

scheduler = Scheduler(owner)
scheduler.enter_task(biscuit, Task("Morning walk", 30, "high", time="08:00", frequency="daily"))
scheduler.enter_task(mochi, Task("Breakfast", 10, "high", time="07:30", frequency="daily"))
scheduler.enter_task(mochi, Task("Brushing", 15, "medium", time="18:00", frequency="weekly"))
scheduler.enter_task(biscuit, Task("Fetch in the yard", 20, "low", time="16:00"))

if __name__ == "__main__":
    print_todays_schedule(scheduler)
