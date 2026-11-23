
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Task


router = APIRouter(
    prefix="/stats",
    tags=["stats"]
)


@router.get("")
def get_tasks_stats(db: Session = Depends(get_db)) -> dict:
    tasks = db.scalars(select(Task)).all()

    by_quadrant = {
        "Q1": 0,
        "Q2": 0,
        "Q3": 0,
        "Q4": 0
    }

    by_status = {
        "completed": 0,
        "pending": 0
    }

    for task in tasks:
        by_quadrant[task.quadrant] += 1

        if task.completed:
            by_status["completed"] += 1
        else:
            by_status["pending"] += 1

    return {
        "total_tasks": len(tasks),
        "by_quadrant": by_quadrant,
        "by_status": by_status
    }
