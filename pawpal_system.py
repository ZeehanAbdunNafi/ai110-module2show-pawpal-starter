from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class OwnerPreferences:
    earliest_start: int = 8 * 60
    latest_end: int = 20 * 60
    max_tasks: Optional[int] = None
    prefer_categories: List[str] = field(default_factory=list)
    avoid_categories: List[str] = field(default_factory=list)
    avoid_ranges: List[tuple] = field(default_factory=list)

    def update_preferences(
        self,
        earliest_start: Optional[int] = None,
        latest_end: Optional[int] = None,
        max_tasks: Optional[int] = None,
        prefer_categories: Optional[List[str]] = None,
        avoid_categories: Optional[List[str]] = None,
    ) -> None:
        if earliest_start is not None:
            self.earliest_start = earliest_start
        if latest_end is not None:
            self.latest_end = latest_end
        if max_tasks is not None:
            self.max_tasks = max_tasks
        if prefer_categories is not None:
            self.prefer_categories = prefer_categories
        if avoid_categories is not None:
            self.avoid_categories = avoid_categories


@dataclass
class Owner:
    name: str
    preferences: OwnerPreferences = field(default_factory=OwnerPreferences)

    def set_available_time(self, earliest_start: int, latest_end: int) -> None:
        self.preferences.earliest_start = earliest_start
        self.preferences.latest_end = latest_end

    def view_daily_plan(self) -> "DayPlan":
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    breed: Optional[str] = None
    health_notes: Optional[str] = None
    tasks: List["PetCareTask"] = field(default_factory=list)

    def display_pet_info(self) -> str:
        return f"{self.name} ({self.species}, {self.age} yrs)"

    def link_task(self, task: "PetCareTask") -> None:
        self.tasks.append(task)

    def update_details(
        self,
        name: Optional[str] = None,
        species: Optional[str] = None,
        age: Optional[int] = None,
        breed: Optional[str] = None,
        health_notes: Optional[str] = None,
    ) -> None:
        if name is not None:
            self.name = name
        if species is not None:
            self.species = species
        if age is not None:
            self.age = age
        if breed is not None:
            self.breed = breed
        if health_notes is not None:
            self.health_notes = health_notes


@dataclass
class PetCareTask:
    title: str
    duration_minutes: int
    priority: Priority
    status: str = "pending"
    task_type: Optional[str] = None
    deadline: Optional[str] = None
    recurring: bool = False

    def mark_complete(self) -> None:
        self.status = "done"

    def update_task_details(
        self,
        title: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        priority: Optional[Priority] = None,
        status: Optional[str] = None,
        deadline: Optional[str] = None,
    ) -> None:
        if title is not None:
            self.title = title
        if duration_minutes is not None:
            self.duration_minutes = duration_minutes
        if priority is not None:
            self.priority = priority
        if status is not None:
            self.status = status
        if deadline is not None:
            self.deadline = deadline

    def check_fit(self, available_start: int, available_end: int) -> bool:
        return available_start + self.duration_minutes <= available_end


@dataclass
class PlanEntry:
    task: PetCareTask
    start_time: int
    end_time: int

    @property
    def duration(self) -> int:
        return self.end_time - self.start_time


@dataclass
class DayPlan:
    selected_tasks: List[PlanEntry] = field(default_factory=list)
    total_planned_time: int = 0
    explanation: List[str] = field(default_factory=list)

    def display_schedule(self) -> str:
        return "\n".join(
            f"{entry.task.title}: {entry.start_time}-{entry.end_time}"
            for entry in self.selected_tasks
        )

    def calculate_total_time(self) -> int:
        self.total_planned_time = sum(entry.duration for entry in self.selected_tasks)
        return self.total_planned_time

    def show_rationale(self) -> str:
        return "\n".join(self.explanation)

    def update_plan(self, entries: List[PlanEntry]) -> None:
        self.selected_tasks = entries
        self.calculate_total_time()


class Scheduler:
    def __init__(
        self,
        tasks: Optional[List[PetCareTask]] = None,
        available_time: Optional[tuple] = None,
    ) -> None:
        self.tasks = tasks or []
        self.available_time = available_time or (8 * 60, 20 * 60)
        self.scheduling_rules = {}
        self.priority_order = ["high", "medium", "low"]

    def add_task(self, task: PetCareTask) -> None:
        self.tasks.append(task)

    def sort_tasks_by_priority(self) -> List[PetCareTask]:
        return sorted(
            self.tasks,
            key=lambda t: self.priority_order.index(t.priority.value)
            if t.priority.value in self.priority_order
            else 1,
        )

    def filter_tasks_by_constraints(self, owner: Owner) -> List[PetCareTask]:
        pass

    def generate_daily_schedule(self, owner: Owner, pet: Pet) -> DayPlan:
        pass

    def explain_selection(self, plan: DayPlan) -> List[str]:
        pass

    def resolve_conflicts(self, tasks: List[PetCareTask]) -> List[PetCareTask]:
        pass
