from datetime import datetime

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    owner = Owner(name="Jordan")

    mochi = Pet(name="Mochi", species="dog", age=4)
    whiskers = Pet(name="Whiskers", species="cat", age=2)

    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    mochi.add_task(Task(description="Morning walk", duration_minutes=30, frequency="daily"))
    mochi.add_task(Task(description="Feed", duration_minutes=15, frequency="daily"))
    mochi.add_task(Task(description="Brush fur", duration_minutes=20, frequency="weekly"))

    whiskers.add_task(Task(description="Feeding", duration_minutes=10, frequency="daily"))
    whiskers.add_task(Task(description="Play with laser", duration_minutes=15, frequency="daily"))


    scheduler = Scheduler(owner=owner)
    plan = scheduler.generate_schedule(start_time=datetime.now().replace(hour=8, minute=0, second=0, microsecond=0))

    print("Generated schedule:")
    for task in plan:
        print(task.display_task_info())

    print("\nPending tasks:")
    for task in scheduler.get_pending_tasks():
        print(task.display_task_info())

    print("\nCompleted tasks:")
    for task in scheduler.get_completed_tasks():
        print(task.display_task_info())


if __name__ == "__main__":
    main()
