from datetime import time

import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
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

all_tasks = scheduler.get_all_tasks(include_completed=True)
if all_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "Pet": pet.name,
                "Due": task.due_date.isoformat(),
                "Time": task.time or "anytime",
                "Task": task.description,
                "Minutes": task.duration_minutes,
                "Priority": task.priority,
                "Frequency": task.frequency,
                "Done": task.completed,
            }
            for pet, task in all_tasks
        ]
    )
    for warning in scheduler.detect_conflicts():
        st.warning(warning)
elif owner.pets:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    plan = scheduler.generate_plan()
    if not plan and not scheduler.skipped:
        st.info("There are no pending tasks to schedule.")
    else:
        for warning in scheduler.conflicts:
            st.warning(warning)
        if plan:
            st.table(
                [
                    {
                        "Time": task.time or "anytime",
                        "Task": task.description,
                        "Pet": pet.name,
                        "Minutes": task.duration_minutes,
                        "Priority": task.priority,
                    }
                    for pet, task in plan
                ]
            )
        st.markdown("**Why this plan?**")
        st.text(scheduler.explain_plan())
