from pawpal_system import Pet, Task


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