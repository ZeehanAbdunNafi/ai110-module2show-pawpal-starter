import streamlit as st
from datetime import datetime

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ pet care schedule assistant.

This application helps you manage pets, define care tasks, and generate daily schedules.
"""
)

# Initialize session state
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Default Owner")

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(st.session_state.owner)

st.divider()

# Owner section
st.subheader("👤 Owner")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value=st.session_state.owner.name)
    if owner_name != st.session_state.owner.name:
        st.session_state.owner.name = owner_name
        st.success(f"Owner renamed to {owner_name}")

with col2:
    st.info(f"Pets: {len(st.session_state.owner.pets)}")

st.divider()

# Pet management section
st.subheader("🐶 Pets")

col1, col2, col3 = st.columns(3)
with col1:
    new_pet_name = st.text_input("New pet name", value="")
with col2:
    new_pet_species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
with col3:
    new_pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=1)

if st.button("➕ Add Pet"):
    if new_pet_name:
        if st.session_state.owner.get_pet(new_pet_name) is None:
            new_pet = Pet(name=new_pet_name, species=new_pet_species, age=new_pet_age)
            st.session_state.owner.add_pet(new_pet)
            st.success(f"✅ Added {new_pet_name} the {new_pet_species}!")
            st.rerun()
        else:
            st.error(f"Pet '{new_pet_name}' already exists.")
    else:
        st.error("Please enter a pet name.")

# Display current pets
if st.session_state.owner.pets:
    st.write("**Current pets:**")
    for pet_name, pet in st.session_state.owner.pets.items():
        st.write(f"  • {pet_name} ({pet.species}, {pet.age} yrs) - {len(pet.tasks)} tasks")
else:
    st.info("No pets yet. Add one to get started!")

st.divider()

# Task management section
st.subheader("📋 Tasks")

if st.session_state.owner.pets:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        selected_pet = st.selectbox(
            "Select pet",
            options=list(st.session_state.owner.pets.keys()),
        )
    with col2:
        task_description = st.text_input("Task description", value="")
    with col3:
        task_duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=30
        )
    with col4:
        task_frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

    if st.button("➕ Add Task"):
        if task_description:
            pet = st.session_state.owner.get_pet(selected_pet)
            if pet:
                new_task = Task(
                    description=task_description,
                    duration_minutes=int(task_duration),
                    frequency=task_frequency,
                )
                pet.add_task(new_task)
                st.success(f"✅ Added task '{task_description}' to {selected_pet}!")
                st.rerun()
        else:
            st.error("Please enter a task description.")

    # Display all tasks sorted by scheduled time
    all_tasks = st.session_state.scheduler.sort_tasks_by_scheduled_time()
    if all_tasks:
        st.write("**All Tasks (Sorted by Scheduled Time):**")
        pending_tasks = [t for t in all_tasks if not t.completed]
        completed_tasks = [t for t in all_tasks if t.completed]

        if pending_tasks:
            st.markdown("**Pending Tasks:**")
            task_data = []
            for task in pending_tasks:
                time_str = task.scheduled_time.strftime("%Y-%m-%d %H:%M") if task.scheduled_time else "Unscheduled"
                task_data.append({
                    "Description": task.description,
                    "Duration (min)": task.duration_minutes,
                    "Frequency": task.frequency,
                    "Scheduled": time_str
                })
            st.table(task_data)

        if completed_tasks:
            st.markdown("**Completed Tasks:**")
            task_data = []
            for task in completed_tasks:
                time_str = task.scheduled_time.strftime("%Y-%m-%d %H:%M") if task.scheduled_time else "Unscheduled"
                task_data.append({
                    "Description": task.description,
                    "Duration (min)": task.duration_minutes,
                    "Frequency": task.frequency,
                    "Scheduled": time_str
                })
            st.table(task_data)
    else:
        st.info("No tasks yet.")
else:
    st.info("Add a pet first to create tasks.")

st.divider()

# Conflict check
conflicts = st.session_state.scheduler.check_conflicts()
if conflicts:
    st.warning("⚠️ Current Scheduling Conflicts:")
    for conflict in conflicts:
        st.write(f"- {conflict}")
else:
    st.info("No scheduling conflicts detected.")

st.divider()

# Schedule generation section
st.subheader("📅 Daily Schedule")

if st.button("🎯 Generate Schedule"):
    all_tasks = st.session_state.scheduler.get_all_tasks()
    
    if not all_tasks:
        st.warning("No tasks available. Add tasks to pets first.")
    else:
        pending_tasks = st.session_state.scheduler.get_pending_tasks()
        
        if not pending_tasks:
            st.info("All tasks are completed! Great job!")
        else:
            # Generate schedule
            schedule, conflicts = st.session_state.scheduler.generate_schedule(
                start_time=datetime.now().replace(hour=8, minute=0, second=0, microsecond=0),
                break_minutes=10,
                max_daily_minutes=8 * 60,
            )

            st.success("✅ Schedule generated!")

            # Display conflicts if any
            if conflicts:
                st.warning("⚠️ Scheduling conflicts detected:")
                for conflict in conflicts:
                    st.write(f"- {conflict}")

            # Display schedule in table format
            if schedule:
                st.markdown("#### Scheduled Tasks")
                schedule_data = []
                for task in schedule:
                    if task.scheduled_time:
                        time_str = task.scheduled_time.strftime("%H:%M")
                    else:
                        time_str = "N/A"
                    
                    schedule_data.append(
                        {
                            "Time": time_str,
                            "Task": task.description,
                            "Duration (min)": task.duration_minutes,
                            "Frequency": task.frequency,
                        }
                    )
                
                st.table(schedule_data)
            else:
                st.warning("Could not schedule any tasks within the time constraints.")

            # Display pending but unscheduled tasks
            unscheduled = [t for t in pending_tasks if t not in schedule]
            if unscheduled:
                st.markdown("#### Pending (Not Scheduled)")
                unscheduled_data = [
                    {
                        "Task": t.description,
                        "Duration (min)": t.duration_minutes,
                        "Frequency": t.frequency,
                    }
                    for t in unscheduled
                ]
                st.table(unscheduled_data)
else:
    st.info("Click 'Generate Schedule' to create your daily plan.")

st.divider()

# Stats footer
total_tasks = len(st.session_state.scheduler.get_all_tasks())
completed_tasks = len(st.session_state.scheduler.get_completed_tasks())
pending_tasks = len(st.session_state.scheduler.get_pending_tasks())

st.markdown(
    f"**Summary:** {completed_tasks}/{total_tasks} tasks completed | {pending_tasks} pending"
)
