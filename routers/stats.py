
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models import Task, User, UserRole
from schemas import TimingStatsResponse
from utils import calculate_days_until_deadline


router = APIRouter(
    prefix="/stats",
    tags=["stats"]
)


def get_user_tasks(
    db: Session,
    user: User
):
    query = select(Task)

    if user.role != UserRole.ADMIN.value:
        query = query.where(
            Task.user_id == user.id
        )

    return db.scalars(query).all()


@router.get("")
def get_tasks_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tasks = get_user_tasks(db, current_user)

    quadrants = {
        "Q1": 0,
        "Q2": 0,
        "Q3": 0,
        "Q4": 0
    }

    completed = 0

    for task in tasks:
        quadrants[task.quadrant] += 1

        if task.completed:
            completed += 1

    return {
        "total_tasks": len(tasks),
        "by_quadrant": quadrants,
        "by_status": {
            "completed": completed,
            "pending": len(tasks) - completed
        }
    }


@router.get("/deadlines")
def get_deadline_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tasks = get_user_tasks(db, current_user)

    pending = [
        task
        for task in tasks
        if not task.completed
    ]

    pending.sort(
        key=lambda t: (
            t.deadline_at is None,
            t.deadline_at or date.max,
            t.id
        )
    )

    return {
        "total_pending": len(pending),
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "created_at": task.created_at,
                "deadline_at": task.deadline_at,
                "days_until_deadline": (
                    calculate_days_until_deadline(
                        task.deadline_at
                    )
                )
            }
            for task in pending
        ]
    }


@router.get(
    "/timing",
    response_model=TimingStatsResponse
)
def get_timing_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tasks = get_user_tasks(db, current_user)
    today = date.today()

    completed_on_time = 0
    completed_late = 0
    on_plan_pending = 0
    overtime_pending = 0

    for task in tasks:
        if task.deadline_at is None:
            continue

        if task.completed:
            if task.completed_at is None:
                continue

            if task.completed_at.date() <= task.deadline_at:
                completed_on_time += 1
            else:
                completed_late += 1

        elif task.deadline_at < today:
            overtime_pending += 1

        else:
            on_plan_pending += 1

    return TimingStatsResponse(
        completed_on_time=completed_on_time,
        completed_late=completed_late,
        on_plan_pending=on_plan_pending,
        overtime_pending=overtime_pending
    )
