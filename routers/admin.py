
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_admin
from models import User, Task


router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    rows = db.execute(
        select(
            User.id,
            User.nickname,
            User.email,
            User.role,
            func.count(Task.id).label("tasks_count")
        )
        .outerjoin(Task, Task.user_id == User.id)
        .group_by(
            User.id,
            User.nickname,
            User.email,
            User.role
        )
        .order_by(User.id)
    ).all()

    users = [
        {
            "id": row.id,
            "nickname": row.nickname,
            "email": row.email,
            "role": row.role,
            "tasks_count": row.tasks_count
        }
        for row in rows
    ]

    return {
        "total_users": len(users),
        "users": users
    }
