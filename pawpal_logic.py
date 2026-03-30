from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple


def minutes_to_clock(mins: int) -> str:
    h = mins // 60
    m = mins % 60
    return f"{h:02d}:{m:02d}"


def clock_to_minutes(t: str) -> int:
    parts = t.split(":")
    if len(parts) != 2:
        raise ValueError("Time should be HH:MM")
    return int(parts[0]) * 60 + int(parts[1])


class Priority(Enum):
    low = 1
    medium = 2
    high = 3


@dataclass
class PetCareTask:
    title: str
    duration_minutes: int
    priority: Priority
    category: str = "general"   # e.g., walk, feed, meds, grooming, enrichment
    details: str = ""

    def __post_init__(self):
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")


@dataclass
class OwnerPreferences:
    earliest_start: int = 8 * 60
    latest_end: int = 20 * 60
    avoid_ranges: List[Tuple[int, int]] = field(default_factory=list)
    max_tasks: Optional[int] = None
    prefer_categories: List[str] = field(default_factory=list)
    avoid_categories: List[str] = field(default_factory=list)


@dataclass
class Owner:
    name: str
    preferences: OwnerPreferences


@dataclass
class Pet:
    name: str
    species: str
    age_years: Optional[float] = None


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
    owner: Owner
    pet: Pet
    entries: List[PlanEntry] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    explanation: List[str] = field(default_factory=list)

    def total_booked_minutes(self) -> int:
        return sum(entry.duration for entry in self.entries)


class Scheduler:
    @staticmethod
    def _is_conflict(start: int, end: int, avoid_ranges: List[Tuple[int, int]]) -> bool:
        for a_start, a_end in avoid_ranges:
            if start < a_end and end > a_start:
                return True
        return False

    @staticmethod
    def _fits_in_range(start: int, end: int, ranges: List[Tuple[int, int]]) -> bool:
        return start >= ranges[0][0] and end <= ranges[0][1]

    @staticmethod
    def build_daily_plan(
        tasks: List[PetCareTask],
        owner: Owner,
        pet: Pet,
        min_task_gap_minutes: int = 10,
    ) -> DayPlan:
        prefs = owner.preferences
        day_plan = DayPlan(owner=owner, pet=pet)

        if prefs.earliest_start >= prefs.latest_end:
            raise ValueError("earliest_start must be before latest_end")

        available_ranges = [(prefs.earliest_start, prefs.latest_end)]

        # Build avoid ranges inside available range (trim to day boundaries)
        blocked = []
        for bstart, bend in prefs.avoid_ranges:
            if bend <= prefs.earliest_start or bstart >= prefs.latest_end:
                continue
            blocked.append((max(bstart, prefs.earliest_start), min(bend, prefs.latest_end)))

        # Sort tasks by priority high->low then shorter duration first
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (-(t.priority.value), t.duration_minutes),
        )

        current_time = prefs.earliest_start

        for task in sorted_tasks:
            if prefs.max_tasks is not None and len(day_plan.entries) >= prefs.max_tasks:
                reason = f"Skipped '{task.title}' (max_tasks reached {prefs.max_tasks})"
                day_plan.skipped.append(task.title)
                day_plan.explanation.append(reason)
                continue

            if prefs.prefer_categories and task.category not in prefs.prefer_categories:
                reason = f"Skipped '{task.title}' (category '{task.category}' not in preferred categories)"
                day_plan.skipped.append(task.title)
                day_plan.explanation.append(reason)
                continue

            if task.category in prefs.avoid_categories:
                reason = f"Skipped '{task.title}' (category '{task.category}' is avoided)"
                day_plan.skipped.append(task.title)
                day_plan.explanation.append(reason)
                continue

            # find next feasible start time after current_time
            candidate_start = max(current_time, prefs.earliest_start)
            candidate_end = candidate_start + task.duration_minutes
            while candidate_end <= prefs.latest_end:
                conflict = Scheduler._is_conflict(candidate_start, candidate_end, blocked)
                if conflict:
                    # move to end of the conflicting block
                    conflicting_blocks = [x for x in blocked if candidate_start < x[1] and candidate_end > x[0]]
                    if not conflicting_blocks:
                        break
                    candidate_start = max(b[1] for b in conflicting_blocks)
                    if min_task_gap_minutes:
                        candidate_start += min_task_gap_minutes
                    candidate_end = candidate_start + task.duration_minutes
                    continue
                # if in day boundary, accept
                if candidate_end <= prefs.latest_end:
                    entry = PlanEntry(task=task, start_time=candidate_start, end_time=candidate_end)
                    day_plan.entries.append(entry)
                    reason = (
                        f"Scheduled '{task.title}' ({task.category}) at {minutes_to_clock(candidate_start)} "
                        f"for {task.duration_minutes} min. Priority {task.priority.name}."
                    )
                    day_plan.explanation.append(reason)
                    current_time = candidate_end + min_task_gap_minutes
                    break
                break
            else:
                # unreachable, but keep safe
                pass

            if not any(entry.task == task for entry in day_plan.entries):
                day_plan.skipped.append(task.title)
                day_plan.explanation.append(
                    f"Could not schedule '{task.title}' due to time constraints (not enough remaining window)"
                )

        # Explain why window includes spare time
        free_time = prefs.latest_end - current_time if current_time < prefs.latest_end else 0
        if free_time > 0:
            day_plan.explanation.append(
                f"Remaining free time after scheduling: {free_time} minutes (from {minutes_to_clock(current_time)} to {minutes_to_clock(prefs.latest_end)})."
            )

        return day_plan


def safe_priority(value: str) -> Priority:
    mapping = {
        "low": Priority.low,
        "medium": Priority.medium,
        "high": Priority.high,
    }
    return mapping.get(value.lower(), Priority.medium)
