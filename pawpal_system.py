from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional


@dataclass
class Task:
    description: str
    duration_minutes: int
    frequency: str = "once"  # e.g., 'once', 'daily', 'weekly'
    completed: bool = False
    scheduled_time: Optional[datetime] = None

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def update_details(
        self,
        description: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        frequency: Optional[str] = None,
        scheduled_time: Optional[datetime] = None,
    ) -> None:
        """Update task details such as description, duration, frequency, or scheduled time."""
        if description is not None:
            self.description = description
        if duration_minutes is not None:
            self.duration_minutes = duration_minutes
        if frequency is not None:
            self.frequency = frequency
        if scheduled_time is not None:
            self.scheduled_time = scheduled_time

    def display_task_info(self) -> str:
        """Return a formatted string with task description, duration, frequency, status, and schedule."""
        status = "Done" if self.completed else "Pending"
        schedule = (
            self.scheduled_time.strftime("%Y-%m-%d %H:%M")
            if self.scheduled_time
            else "Unscheduled"
        )
        return (
            f"Task: {self.description}, duration: {self.duration_minutes} min, "
            f"frequency: {self.frequency}, status: {status}, scheduled: {schedule}"
        )


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, description: str) -> bool:
        """Remove a task by description; return True if found and removed, False otherwise."""
        for i, t in enumerate(self.tasks):
            if t.description == description:
                del self.tasks[i]
                return True
        return False

    def get_tasks(self) -> List[Task]:
        """Return a copy of this pet's task list."""
        return list(self.tasks)

    def update_details(
        self,
        name: Optional[str] = None,
        species: Optional[str] = None,
        age: Optional[int] = None,
    ) -> None:
        """Update pet details such as name, species, or age."""
        if name is not None:
            self.name = name
        if species is not None:
            self.species = species
        if age is not None:
            self.age = age


@dataclass
class Owner:
    name: str
    pets: Dict[str, Pet] = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet collection."""
        self.pets[pet.name] = pet

    def get_pet(self, name: str) -> Optional[Pet]:
        """Retrieve a pet by name; return None if not found."""
        return self.pets.get(name)

    def get_all_tasks(self) -> List[Task]:
        """Return a list of all tasks from all pets owned by this owner."""
        tasks: List[Task] = []
        for pet in self.pets.values():
            tasks.extend(pet.get_tasks())
        return tasks


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        """Initialize scheduler with an owner."""
        self.owner = owner

    def get_all_tasks(self) -> List[Task]:
        """Retrieve all tasks from the owner's pets."""
        return self.owner.get_all_tasks()

    def get_pending_tasks(self) -> List[Task]:
        """Return all incomplete tasks."""
        return [t for t in self.get_all_tasks() if not t.completed]

    def get_completed_tasks(self) -> List[Task]:
        """Return all completed tasks."""
        return [t for t in self.get_all_tasks() if t.completed]

    def sort_tasks_by_time(self) -> List[Task]:
        """Return all tasks sorted by duration in ascending order."""
        return sorted(self.get_all_tasks(), key=lambda t: t.duration_minutes)

    def generate_schedule(
        self,
        start_time: Optional[datetime] = None,
        break_minutes: int = 10,
        max_daily_minutes: int = 8 * 60,
    ) -> List[Task]:
        """Generate a daily schedule of pending tasks sorted by frequency and duration, with breaks between tasks."""
        if start_time is None:
            start_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)

        pending = self.get_pending_tasks()
        freq_rank = {"daily": 1, "weekly": 2, "once": 3}

        pending_sorted = sorted(
            pending,
            key=lambda t: (
                freq_rank.get(t.frequency, 4),
                t.duration_minutes,
            ),
        )

        schedule: List[Task] = []
        current_time = start_time
        allocated_minutes = 0

        for task in pending_sorted:
            if allocated_minutes + task.duration_minutes > max_daily_minutes:
                break

            task.scheduled_time = current_time
            schedule.append(task)
            allocated_minutes += task.duration_minutes
            current_time += timedelta(minutes=task.duration_minutes + break_minutes)

        return schedule