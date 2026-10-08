from datetime import time

import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.caption(
    "Plan your pets' care for the day. PawPal+ picks the most important tasks that fit "
    "your time, puts them in order, and warns you about clashes."
)

st.divider()

# Create the owner and scheduler once, then reuse them on every rerun.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", available_minutes=90)
    st.session_state.scheduler = Scheduler(st.session_state.owner)

owner = st.session_state.owner
scheduler = st.session_state.scheduler

st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value="Jordan")
with col2:
    owner.available_minutes = st.number_input(
        "Minutes available today", min_value=0, max_value=1440, value=90
    )

st.divider()

st.subheader("Add a Pet")
with st.form("add_pet", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        pet_name = st.text_input("Pet name")
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col2:
        breed = st.text_input("Breed (optional)")
        age = st.number_input("Age (years)", min_value=0, max_value=40, value=1)
    add_pet_clicked = st.form_submit_button("Add pet")

if add_pet_clicked:
    pet_name = pet_name.strip()
    if not pet_name:
        st.error("Please enter a pet name.")
    elif owner.get_pet(pet_name) is not None:
        st.warning(f"{pet_name} is already added.")
    else:
        owner.add_pet(Pet(pet_name, species, breed=breed.strip(), age=int(age)))
        st.success(f"Added {pet_name}!")

if owner.pets:
    st.write("Your pets:")
    for pet in owner.pets:
        st.markdown(f"- {pet.get_pet_info()}")
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Schedule a Task")
if not owner.pets:
    st.info("Add a pet before scheduling tasks.")
else:
    with st.form("add_task", clear_on_submit=True):
        task_pet_name = st.selectbox("For which pet?", [pet.name for pet in owner.pets])
        description = st.text_input("Task", placeholder="Morning walk")
        col1, col2, col3 = st.columns(3)
        with col1:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col2:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        with col3:
            frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
        col1, col2 = st.columns(2)
        with col1:
            task_time = st.time_input("Time", value=time(8, 0))
        with col2:
            anytime = st.checkbox("Anytime (no set time)")
        add_task_clicked = st.form_submit_button("Add task")

    if add_task_clicked:
        if not description.strip():
            st.error("Please describe the task.")
        else:
            try:
                task = Task(
                    description.strip(),
                    int(duration),
                    priority,
                    time=None if anytime else task_time.strftime("%H:%M"),
                    frequency=frequency,
                )
                scheduler.enter_task(owner.get_pet(task_pet_name), task)
                st.success(f"Added '{task.description}' for {task_pet_name}.")
            except ValueError as error:
                st.error(str(error))

PRIORITY_LABEL = {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}
CONFLICT_TIP = "Consider moving one of them to a different time so you're not in two places at once."


def task_label(pet, task):
    """Return a short readable label for a task, used in dropdowns."""
    return f"{task.time or 'anytime'} - {task.description} ({pet.name}, due {task.due_date:%b %d})"


st.subheader("Your Tasks")
if scheduler.get_all_tasks(include_completed=True):
    show = st.radio("Show", ["Pending", "Completed", "All"], horizontal=True)
    if show == "All":
        pairs = scheduler.get_all_tasks(include_completed=True)
    else:
        pairs = scheduler.filter_by_status(completed=(show == "Completed"))
    # sort by time first, then by due date; the stable sort keeps time order within each day
    pairs = sorted(scheduler.sort_by_time(pairs), key=lambda pt: pt[1].due_date)

    if pairs:
        st.table(
            [
                {
                    "Due": f"{task.due_date:%b %d}",
                    "Time": task.time or "anytime",
                    "Task": task.description,
                    "Pet": pet.name,
                    "Minutes": task.duration_minutes,
                    "Priority": PRIORITY_LABEL[task.priority],
                    "Repeats": task.frequency,
                    "Status": "✅ done" if task.completed else "⏳ pending",
                }
                for pet, task in pairs
            ]
        )
    else:
        st.info(f"No {show.lower()} tasks.")

    for warning in scheduler.detect_conflicts():
        st.warning(f"{warning} {CONFLICT_TIP}", icon="⚠️")

    pending = scheduler.sort_by_time(scheduler.filter_by_status(completed=False))
    if pending:
        col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
        with col1:
            choice = st.selectbox(
                "Mark a task complete",
                range(len(pending)),
                format_func=lambda i: task_label(*pending[i]),
            )
        with col2:
            complete_clicked = st.button("Mark done", width="stretch")
        if complete_clicked:
            pet, task = pending[choice]
            next_task = scheduler.mark_task_complete(task)
            message = f"Nice! '{task.description}' for {pet.name} is done."
            if next_task is not None:
                message += f" The next one is due {next_task.due_date:%A, %b %d}."
            st.session_state.flash = message
            st.rerun()

    if "flash" in st.session_state:
        st.success(st.session_state.pop("flash"))
elif owner.pets:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Today's Schedule")

if st.button("Generate schedule", type="primary"):
    st.session_state.show_plan = True

# Keep showing the plan after it's generated, rebuilding it so it reflects any changes.
if st.session_state.get("show_plan"):
    plan = scheduler.generate_plan()
    if not plan and not scheduler.skipped:
        st.info("Nothing left to schedule today. 🎉")
    else:
        # Conflicts go first so the owner sees them before reading the plan.
        for warning in scheduler.conflicts:
            st.warning(f"**Time clash:** {warning} {CONFLICT_TIP}", icon="⚠️")

        used = sum(task.duration_minutes for _, task in plan)
        budget = owner.available_minutes
        if not scheduler.skipped:
            st.success(f"Everything fits! {len(plan)} task(s) using {used} of {budget} minutes.")
        st.progress(min(used / budget, 1.0) if budget else 1.0, text=f"{used} / {budget} minutes planned")

        # Count tasks per (date, time) slot so clashing rows can be marked in the table.
        slot_counts = {}
        for _, task in plan:
            if task.time:
                slot = (task.due_date, task.time)
                slot_counts[slot] = slot_counts.get(slot, 0) + 1

        if plan:
            st.table(
                [
                    {
                        "Time": task.time or "anytime",
                        "Task": task.description,
                        "Pet": pet.name,
                        "Minutes": task.duration_minutes,
                        "Priority": PRIORITY_LABEL[task.priority],
                        "Note": "⚠️ clash" if slot_counts.get((task.due_date, task.time), 0) > 1 else "",
                    }
                    for pet, task in plan
                ]
            )

        if scheduler.skipped:
            st.warning(
                f"{len(scheduler.skipped)} task(s) didn't fit in your {budget} minutes. "
                "Higher-priority tasks were scheduled first.",
                icon="⏰",
            )
            st.table(
                [
                    {
                        "Task": task.description,
                        "Pet": pet.name,
                        "Minutes": task.duration_minutes,
                        "Priority": PRIORITY_LABEL[task.priority],
                    }
                    for pet, task in scheduler.skipped
                ]
            )

        with st.expander("Why this plan?"):
            st.text(scheduler.explain_plan())
