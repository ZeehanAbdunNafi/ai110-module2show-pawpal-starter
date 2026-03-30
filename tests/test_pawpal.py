from datetime import datetime, timedelta
from pawpal_system import Pet, Task, Owner, Scheduler


def test_mark_complete_changes_status():
    task = Task(description="Feed", duration_minutes=15, frequency="daily")
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", age=4)
    task = Task(description="Walk", duration_minutes=30, frequency="daily")

    initial_count = len(pet.tasks)
    pet.add_task(task)

    assert len(pet.tasks) == initial_count + 1


def test_sort_tasks_by_scheduled_time():
    """Verify tasks are sorted chronologically by scheduled time, with unscheduled tasks last."""
    owner = Owner(name="Alice")
    pet = Pet(name="Mochi", species="dog", age=4)
    owner.add_pet(pet)

    # Create tasks with different scheduled times
    task1 = Task(description="Morning walk", duration_minutes=30, scheduled_time=datetime(2023, 10, 1, 8, 0))
    task2 = Task(description="Evening feed", duration_minutes=15, scheduled_time=datetime(2023, 10, 1, 18, 0))
    task3 = Task(description="Unscheduled grooming", duration_minutes=45)  # No scheduled_time

    pet.add_task(task1)
    pet.add_task(task2)
    pet.add_task(task3)

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_tasks_by_scheduled_time()

    # Assert order: earliest first, unscheduled last
    assert sorted_tasks[0].description == "Morning walk"
    assert sorted_tasks[1].description == "Evening feed"
    assert sorted_tasks[2].description == "Unscheduled grooming"


def test_recurring_task_creates_next_occurrence():
    """Verify marking a daily task complete creates a new task for the next day."""
    owner = Owner(name="Alice")
    pet = Pet(name="Mochi", species="dog", age=4)
    owner.add_pet(pet)

    initial_time = datetime(2023, 10, 1, 8, 0)
    task = Task(description="Daily feed", duration_minutes=15, frequency="daily", scheduled_time=initial_time)
    pet.add_task(task)

    scheduler = Scheduler(owner)
    scheduler.mark_task_complete(task)

    # Check original task is completed
    assert task.completed is True

    # Check a new task was added
    tasks = pet.get_tasks()
    assert len(tasks) == 2

    # Find the new task
    new_task = next(t for t in tasks if t != task)
    assert new_task.description == "Daily feed"
    assert new_task.frequency == "daily"
    assert new_task.scheduled_time == initial_time + timedelta(days=1)
    assert new_task.completed is False


def test_conflict_detection_flags_duplicate_times():
    """Verify Scheduler detects conflicts when tasks have the same scheduled time."""
    owner = Owner(name="Alice")
    pet = Pet(name="Mochi", species="dog", age=4)
    owner.add_pet(pet)

    conflict_time = datetime(2023, 10, 1, 8, 0)
    task1 = Task(description="Quick grooming", duration_minutes=20, scheduled_time=conflict_time)
    task2 = Task(description="Feeding", duration_minutes=15, scheduled_time=conflict_time)

    pet.add_task(task1)
    pet.add_task(task2)

    scheduler = Scheduler(owner)
    conflicts = scheduler.check_conflicts()

    # Should detect one conflict
    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]
    assert "Quick grooming" in conflicts[0]
    assert "Feeding" in conflicts[0]


def test_filter_tasks_by_status():
    """Verify filtering tasks by completion status works correctly."""
    owner = Owner(name="Alice")
    pet = Pet(name="Mochi", species="dog", age=4)
    owner.add_pet(pet)

    task1 = Task(description="Walk", duration_minutes=30, completed=False)
    task2 = Task(description="Feed", duration_minutes=15, completed=True)

    pet.add_task(task1)
    pet.add_task(task2)

    scheduler = Scheduler(owner)

    pending = scheduler.filter_tasks_by_status(completed=False)
    completed = scheduler.filter_tasks_by_status(completed=True)

    assert len(pending) == 1
    assert pending[0].description == "Walk"

    assert len(completed) == 1
    assert completed[0].description == "Feed"


def test_filter_tasks_by_pet_no_tasks():
    """Edge case: Verify filtering tasks for a pet with no tasks returns empty list."""
    owner = Owner(name="Alice")
    pet = Pet(name="Mochi", species="dog", age=4)
    owner.add_pet(pet)  # Pet has no tasks

    scheduler = Scheduler(owner)
    tasks = scheduler.filter_tasks_by_pet("Mochi")

    assert tasks == []


def test_filter_tasks_by_nonexistent_pet():
    """Edge case: Verify filtering tasks for a non-existent pet returns empty list."""
    owner = Owner(name="Alice")
    scheduler = Scheduler(owner)
    tasks = scheduler.filter_tasks_by_pet("NonExistentPet")

    assert tasks == []