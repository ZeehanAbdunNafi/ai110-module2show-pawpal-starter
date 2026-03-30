import streamlit as st
from datetime import time

from pawpal_logic import Owner, OwnerPreferences, Pet, PetCareTask, Scheduler, safe_priority

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ pet care schedule assistant.

This application tracks tasks, constraints, and produces a explainable daily plan for pet owners.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
- Pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Constraints: time available, priorities, owner preferences
- Daily plan output + explanation why each assignment was chosen
"""
    )

st.divider()

st.subheader("Owner + Pet Info")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Daily scheduling constraints")
col1, col2 = st.columns(2)
with col1:
    earliest = st.time_input("Earliest start time", value=time(8, 0))
with col2:
    latest = st.time_input("Latest end time", value=time(20, 0))

max_tasks = st.slider("Max tasks per day", min_value=1, max_value=20, value=10)

st.markdown("### Preferences")
prefer_grooming = st.checkbox("Prefer grooming/enrichment tasks first", value=False)
avoid_meds = st.checkbox("Avoid medication if possible", value=False)

prefer_categories = []
avoid_categories = []
if prefer_grooming:
    prefer_categories = ["grooming", "enrichment"]
if avoid_meds:
    avoid_categories = ["meds"]

st.divider()

st.subheader("Tasks")
if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority_value = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    category = st.selectbox("Category", ["walk", "feeding", "meds", "enrichment", "grooming", "general"], index=0)

if st.button("Add task"):
    st.session_state.tasks.append(
        {
            "title": task_title,
            "duration_minutes": int(duration),
            "priority": priority_value,
            "category": category,
        }
    )

if st.session_state.tasks:
    st.write("Current tasks")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.error("Add at least one task before generating a schedule.")
    else:
        owner = Owner(
            name=owner_name,
            preferences=OwnerPreferences(
                earliest_start=earliest.hour * 60 + earliest.minute,
                latest_end=latest.hour * 60 + latest.minute,
                max_tasks=max_tasks,
                prefer_categories=prefer_categories,
                avoid_categories=avoid_categories,
            ),
        )
        pet = Pet(name=pet_name, species=species)

        tasks = []
        for t in st.session_state.tasks:
            tasks.append(
                PetCareTask(
                    title=t["title"],
                    duration_minutes=int(t["duration_minutes"]),
                    priority=safe_priority(t["priority"]),
                    category=t.get("category", "general"),
                )
            )

        day_plan = Scheduler.build_daily_plan(tasks=tasks, owner=owner, pet=pet)

        st.success("Daily plan generated ✅")

        st.markdown("### Schedule")
        if day_plan.entries:
            table_data = []
            for e in day_plan.entries:
                table_data.append(
                    {
                        "Task": e.task.title,
                        "Category": e.task.category,
                        "Priority": e.task.priority.name,
                        "Start": f"{e.start_time // 60:02d}:{e.start_time % 60:02d}",
                        "End": f"{e.end_time // 60:02d}:{e.end_time % 60:02d}",
                        "Duration (min)": e.duration,
                    }
                )
            st.table(table_data)
        else:
            st.warning("No tasks could be scheduled within the constraints.")

        if day_plan.skipped:
            st.markdown("### Skipped tasks")
            st.write(day_plan.skipped)

        st.markdown("### Why this schedule?")
        for reason in day_plan.explanation:
            st.write(f"- {reason}")
