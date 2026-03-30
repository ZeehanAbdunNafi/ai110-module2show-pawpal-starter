from datetime import datetime

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    owner = Owner(name="Jordan")

    mochi = Pet(name="Mochi", species="dog", age=4)
    whiskers = Pet(name="Whiskers", species="cat", age=2)

    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    # Add tasks out of order (longer durations first)
    mochi.add_task(Task(description="Brush fur", duration_minutes=20, frequency="weekly"))
    mochi.add_task(Task(description="Morning walk", duration_minutes=30, frequency="daily"))
    mochi.add_task(Task(description="Feed", duration_minutes=15, frequency="daily"))

    whiskers.add_task(Task(description="Feeding", duration_minutes=10, frequency="daily"))
    whiskers.add_task(Task(description="Play with laser", duration_minutes=15, frequency="daily"))

    # Add conflicting tasks (same time manually)
    mochi.add_task(Task(description="Quick grooming", duration_minutes=10, frequency="daily", scheduled_time=datetime.now().replace(hour=8, minute=0)))
    mochi.add_task(Task(description="Another task", duration_minutes=5, frequency="once", scheduled_time=datetime.now().replace(hour=8, minute=0)))

    scheduler = Scheduler(owner=owner)
    plan, schedule_conflicts = scheduler.generate_schedule(start_time=datetime.now().replace(hour=8, minute=0, second=0, microsecond=0))

    print("Generated schedule:")
    for task in plan:
        print(task.display_task_info())

    if schedule_conflicts:
        print("\nConflicts detected in schedule:")
        for conflict in schedule_conflicts:
            print(f"⚠️ {conflict}")

    # Force a conflict for demo purposes
    if len(plan) >= 2:
        plan[1].scheduled_time = plan[0].scheduled_time

    # Check for conflicts in all tasks (including manually scheduled)
    all_conflicts = scheduler.check_conflicts()
    if all_conflicts:
        print("\nConflicts in all tasks (after forcing demo conflict):")
        for conflict in all_conflicts:
            print(f"⚠️ {conflict}")

    print("\nAll tasks sorted by scheduled time:")
    sorted_tasks = scheduler.sort_tasks_by_scheduled_time()
    for task in sorted_tasks:
        print(task.display_task_info())

    print("\nFiltered: Pending tasks only:")
    pending = scheduler.filter_tasks_by_status(completed=False)
    for task in pending:
        print(task.display_task_info())

    print("\nFiltered: Tasks for Mochi only:")
    mochi_tasks = scheduler.filter_tasks_by_pet("Mochi")
    for task in mochi_tasks:
        print(task.display_task_info())

    # Demonstrate recurring tasks
    print("\nBefore marking complete:")
    for task in scheduler.get_all_tasks():
        print(task.display_task_info())

    # Mark a daily task complete to trigger recurring
    daily_task = next((t for t in scheduler.get_all_tasks() if t.description == "Morning walk"), None)
    if daily_task:
        scheduler.mark_task_complete(daily_task)

    print("\nAfter marking 'Morning walk' complete (recurring added):")
    for task in scheduler.get_all_tasks():
        print(task.display_task_info())

    print("\nPending tasks:")
    for task in scheduler.get_pending_tasks():
        print(task.display_task_info())

    print("\nCompleted tasks:")
    for task in scheduler.get_completed_tasks():
        print(task.display_task_info())


if __name__ == "__main__":
    main()
