
from datetime import date
from typing import Optional


def calculate_days_until_deadline(
    deadline_at: Optional[date]
) -> Optional[int]:
    if deadline_at is None:
        return None

    return (deadline_at - date.today()).days


def calculate_urgency(
    deadline_at: Optional[date]
) -> bool:
    days_left = calculate_days_until_deadline(deadline_at)

    if days_left is None:
        return False

    return days_left <= 3


def determine_quadrant(
    is_important: bool,
    is_urgent: bool
) -> str:
    if is_important and is_urgent:
        return "Q1"

    if is_important:
        return "Q2"

    if is_urgent:
        return "Q3"

    return "Q4"
