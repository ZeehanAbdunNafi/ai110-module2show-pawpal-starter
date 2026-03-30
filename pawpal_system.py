from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


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

    def create_next_occurrence(self) -> Optional["Task"]:
        """Create next occurrence for recurring tasks."""
        if self.frequency == "daily" and self.scheduled_time:
            next_time = self.scheduled_time + timedelta(days=1)
            return Task(
                description=self.description,
                duration_minutes=self.duration_minutes,
                frequency=self.frequency,
                scheduled_time=next_time,
            )
        elif self.frequency == "weekly" and self.scheduled_time:
            next_time = self.scheduled_time + timedelta(days=7)
            return Task(
                description=self.description,
                duration_minutes=self.duration_minutes,
                frequency=self.frequency,
                scheduled_time=next_time,
            )
        return None


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

    def sort_tasks_by_duration(self) -> List[Task]:
        """Return all tasks sorted by duration in ascending order."""
        return sorted(self.get_all_tasks(), key=lambda t: t.duration_minutes)

    def sort_tasks_by_scheduled_time(self) -> List[Task]:
        """Return all tasks sorted by scheduled_time (earliest first, unscheduled last)."""
        return sorted(
            self.get_all_tasks(),
            key=lambda t: t.scheduled_time if t.scheduled_time else datetime.max
        )

    def filter_tasks_by_status(self, completed: bool) -> List[Task]:
        """Return tasks filtered by completion status."""
        return [t for t in self.get_all_tasks() if t.completed == completed]

    def filter_tasks_by_pet(self, pet_name: str) -> List[Task]:
        """Return tasks for a specific pet by name."""
        pet = self.owner.get_pet(pet_name)
        return pet.get_tasks() if pet else []

    def generate_schedule(
        self,
        start_time: Optional[datetime] = None,
        break_minutes: int = 10,
        max_daily_minutes: int = 8 * 60,
    ) -> Tuple[List[Task], List[str]]:
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

        # Detect conflicts: group by scheduled_time
        time_groups = {}
        for task in schedule:
            if task.scheduled_time:
                key = task.scheduled_time
                if key not in time_groups:
                    time_groups[key] = []
                time_groups[key].append(task)

        conflicts = []
        for time_key, tasks_at_time in time_groups.items():
            if len(tasks_at_time) > 1:
                task_names = [t.description for t in tasks_at_time]
                conflicts.append(f"Conflict at {time_key.strftime('%H:%M')}: {', '.join(task_names)}")

        return schedule, conflicts


    def check_conflicts(self) -> List[str]:
        """Check for conflicts in currently scheduled tasks."""
        time_groups = {}
        for task in self.get_all_tasks():
            if task.scheduled_time and not task.completed:
                key = task.scheduled_time
                if key not in time_groups:
                    time_groups[key] = []
                time_groups[key].append(task)

        conflicts = []
        for time_key, tasks_at_time in time_groups.items():
            if len(tasks_at_time) > 1:
                task_names = [t.description for t in tasks_at_time]
                conflicts.append(f"Conflict at {time_key.strftime('%H:%M')}: {', '.join(task_names)}")

        return conflicts


    def mark_task_complete(self, task: Task) -> None:
        """Mark a task complete and handle recurring tasks."""
        task.mark_complete()
        if task.frequency in ["daily", "weekly"]:
            next_task = task.create_next_occurrence()
            if next_task:
                # Find the pet and add the next task
                for pet in self.owner.pets.values():
                    if task in pet.tasks:
                        pet.add_task(next_task)
                        break