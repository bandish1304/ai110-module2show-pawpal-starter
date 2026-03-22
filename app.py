import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

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

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Ben")
pet_name = st.text_input("Pet name", value="Jack")
species = st.selectbox("Species", ["dog", "cat", "other"])

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)

owner = st.session_state.owner
owner.name = owner_name

if "task_counter" not in st.session_state:
    st.session_state.task_counter = 1

if st.button("Add pet"):
    try:
        owner.add_pet(Pet(name=pet_name, species=species))
        st.success(f"Added pet: {pet_name}")
    except ValueError as error:
        st.info(str(error))

pets = owner.get_pets()
pet_names = [pet.name for pet in pets]

if pets:
    st.write("Current pets:")
    st.table([{"name": pet.name, "species": pet.species} for pet in pets])
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

selected_pet_name = st.selectbox("Assign task to pet", pet_names, disabled=not pet_names)

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task", disabled=not pet_names):
    pet = owner.get_pet(selected_pet_name)
    if pet is None:
        st.error("Selected pet was not found.")
    else:
        task_id = f"task-{st.session_state.task_counter}"
        st.session_state.task_counter += 1
        try:
            pet.add_task(
                Task(
                    task_id=task_id,
                    title=task_title,
                    duration_minutes=int(duration),
                    priority=priority,
                )
            )
            st.success(f"Added task '{task_title}' for {pet.name}")
        except ValueError as error:
            st.error(str(error))

all_tasks = []
for pet in owner.get_pets():
    for task in pet.get_tasks():
        all_tasks.append(
            {
                "pet": pet.name,
                "title": task.title,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
            }
        )

if all_tasks:
    st.write("Current tasks:")
    st.table(all_tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    if not owner.get_pets():
        st.warning("Add at least one pet before generating a schedule.")
    elif not owner.get_all_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(owner)
        scheduled_tasks = scheduler.generate_schedule()
        if scheduled_tasks:
            st.success("Schedule generated.")
            scheduled_table = []
            for task in scheduled_tasks:
                scheduled_table.append(
                    {
                        "title": task.title,
                        "duration_minutes": task.duration_minutes,
                        "priority": task.priority,
                    }
                )
            st.table(scheduled_table)
        else:
            st.info("No tasks could be scheduled with current constraints.")

        st.text(scheduler.explain_schedule())
