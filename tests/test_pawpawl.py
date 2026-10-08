from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_task_status():
    task = Task("Morning walk", 30, "high", time="08:00")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Biscuit", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Breakfast", 10, "high", time="07:30"))

    assert len(pet.tasks) == 1


def test_sort_by_time_handles_single_digit_hours():
    owner = Owner("Jordan", 90)
    pet = Pet("Biscuit", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Evening walk", 30, time="10:00"))
    pet.add_task(Task("Breakfast", 10, time="8:00"))
    pet.add_task(Task("Play", 15))  # no time, so it should go last

    ordered = Scheduler(owner).sort_by_time(owner.get_all_tasks())

    assert [task.time for _, task in ordered] == ["08:00", "10:00", None]


def test_filter_by_status_separates_completed_and_pending_tasks():
    owner = Owner("Jordan", 90)
    biscuit = Pet("Biscuit", "dog")
    mochi = Pet("Mochi", "cat")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)
    walk = Task("Morning walk", 30)
    breakfast = Task("Breakfast", 10)
    brushing = Task("Brushing", 15)
    biscuit.add_task(walk)
    mochi.add_task(breakfast)
    mochi.add_task(brushing)
    breakfast.mark_complete()
    scheduler = Scheduler(owner)

    done = [task for _, task in scheduler.filter_by_status(completed=True)]
    pending = [task for _, task in scheduler.filter_by_status(completed=False)]

    assert done == [breakfast]
    assert pending == [walk, brushing]
    assert mochi.get_completed_tasks() == [breakfast]
    assert mochi.get_pending_tasks() == [brushing]


def test_completing_daily_task_creates_one_for_tomorrow():
    owner = Owner("Jordan", 90)
    pet = Pet("Biscuit", "dog")
    owner.add_pet(pet)
    walk = Task("Morning walk", 30, "high", time="08:00", frequency="daily")
    pet.add_task(walk)

    next_walk = Scheduler(owner).mark_task_complete(walk)

    assert walk.completed is True
    assert next_walk.completed is False
    assert next_walk.due_date == walk.due_date + timedelta(days=1)
    assert next_walk.time == "08:00"
    assert pet.tasks == [walk, next_walk]


def test_completing_weekly_task_creates_one_for_next_week():
    weekly = Task("Brushing", 15, frequency="weekly", due_date=date(2026, 10, 7))

    assert weekly.next_occurrence().due_date == date(2026, 10, 14)


def test_completing_one_time_task_does_not_repeat():
    owner = Owner("Jordan", 90)
    pet = Pet("Biscuit", "dog")
    owner.add_pet(pet)
    vet = Task("Vet visit", 60)
    pet.add_task(vet)

    assert Scheduler(owner).mark_task_complete(vet) is None
    assert pet.tasks == [vet]


def test_todays_plan_leaves_out_tomorrows_task():
    owner = Owner("Jordan", 90)
    pet = Pet("Biscuit", "dog")
    owner.add_pet(pet)
    walk = Task("Morning walk", 30, frequency="daily")
    pet.add_task(walk)
    scheduler = Scheduler(owner)
    scheduler.mark_task_complete(walk)

    assert scheduler.generate_plan() == []
    assert len(scheduler.generate_plan(day=date.today() + timedelta(days=1))) == 1


def test_detect_conflicts_warns_about_same_time_tasks():
    owner = Owner("Jordan", 90)
    biscuit = Pet("Biscuit", "dog")
    mochi = Pet("Mochi", "cat")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)
    biscuit.add_task(Task("Morning walk", 30, time="08:00"))
    mochi.add_task(Task("Clean litter box", 5, time="8:00"))
    mochi.add_task(Task("Breakfast", 10, time="07:30"))

    warnings = Scheduler(owner).detect_conflicts()

    assert len(warnings) == 1
    assert "08:00" in warnings[0]
    assert "Morning walk" in warnings[0] and "Clean litter box" in warnings[0]


def test_detect_conflicts_ignores_different_days_and_completed_tasks():
    owner = Owner("Jordan", 90)
    pet = Pet("Biscuit", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", 30, time="08:00", due_date=date(2026, 10, 7)))
    pet.add_task(Task("Walk", 30, time="08:00", due_date=date(2026, 10, 8)))
    pet.add_task(Task("Meds", 5, time="08:00", due_date=date(2026, 10, 7), completed=True))

    assert Scheduler(owner).detect_conflicts() == []
