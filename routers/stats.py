
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, case, cast, Date
from sqlalchemy.orm import Session

from database import get_db
from models import Task
from schemas import TimingStatsResponse
from utils import calculate_days_until_deadline


router = APIRouter(
    prefix="/stats",
    tags=["stats"]
)


@router.get("")
def get_tasks_stats(db: Session = Depends(get_db)) -> dict:
    total_tasks = db.scalar(select(func.count(Task.id))) or 0

    quadrant_rows = db.execute(
        select(Task.quadrant, func.count(Task.id))
        .group_by(Task.quadrant)
    ).all()

    by_quadrant = {
        "Q1": 0,
        "Q2": 0,
        "Q3": 0,
        "Q4": 0
    }

    for quadrant, count in quadrant_rows:
        by_quadrant[quadrant] = count

    completed_count = db.scalar(
        select(func.count(Task.id))
        .where(Task.completed.is_(True))
    ) or 0

    return {
        "total_tasks": total_tasks,
        "by_quadrant": by_quadrant,
        "by_status": {
            "completed": completed_count,
            "pending": total_tasks - completed_count
        }
    }


@router.get("/deadlines")
def get_deadline_stats(db: Session = Depends(get_db)) -> dict:
    tasks = db.scalars(
        select(Task)
        .where(Task.completed.is_(False))
        .order_by(Task.deadline_at, Task.id)
    ).all()

    return {
        "total_pending": len(tasks),
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "created_at": task.created_at,
                "deadline_at": task.deadline_at,
                "days_until_deadline": calculate_days_until_deadline(
                    task.deadline_at
                )
            }
            for task in tasks
        ]
    }


@router.get("/timing", response_model=TimingStatsResponse)
def get_timing_stats(
    db: Session = Depends(get_db)
):
    today = date.today()

    statement = select(
        func.count(
            case(
                (
                    (Task.completed.is_(True)) &
                    (Task.deadline_at.is_not(None)) &
                    (Task.completed_at.is_not(None)) &
                    (cast(Task.completed_at, Date) <= Task.deadline_at),
                    1
                )
            )
        ).label("completed_on_time"),

        func.count(
            case(
                (
                    (Task.completed.is_(True)) &
                    (Task.deadline_at.is_not(None)) &
                    (Task.completed_at.is_not(None)) &
                    (cast(Task.completed_at, Date) > Task.deadline_at),
                    1
                )
            )
        ).label("completed_late"),

        func.count(
            case(
                (
                    (Task.completed.is_(False)) &
                    (Task.deadline_at.is_not(None)) &
                    (Task.deadline_at >= today),
                    1
                )
            )
        ).label("on_plan_pending"),

        func.count(
            case(
                (
                    (Task.completed.is_(False)) &
                    (Task.deadline_at.is_not(None)) &
                    (Task.deadline_at < today),
                    1
                )
            )
        ).label("overtime_pending")
    )

    result = db.execute(statement).one()

    return TimingStatsResponse(
        completed_on_time=result.completed_on_time,
        completed_late=result.completed_late,
        on_plan_pending=result.on_plan_pending,
        overtime_pending=result.overtime_pending
    )
