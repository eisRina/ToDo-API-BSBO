
from fastapi import APIRouter
from database import tasks_db


router = APIRouter(
    prefix="/stats",
    tags=["stats"]
)


@router.get("")
async def get_tasks_stats() -> dict:
    return {
        "total_tasks": len(tasks_db),
        "by_quadrant": {
            quadrant: sum(
                1 for task in tasks_db
                if task["quadrant"] == quadrant
            )
            for quadrant in ["Q1", "Q2", "Q3", "Q4"]
        },
        "by_status": {
            "completed": sum(
                1 for task in tasks_db
                if task["completed"]
            ),
            "pending": sum(
                1 for task in tasks_db
                if not task["completed"]
            )
        }
    }
