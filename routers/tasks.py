
from datetime import date, datetime
from typing import List

from fastapi import (
    APIRouter, Depends, HTTPException,
    Query, Response, status
)
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models import Task, User, UserRole
from schemas import TaskCreate, TaskUpdate, TaskResponse
from utils import calculate_urgency, determine_quadrant


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)


def is_admin(user: User) -> bool:
    return user.role == UserRole.ADMIN.value


def visible_tasks(user: User):
    query = select(Task)

    if not is_admin(user):
        query = query.where(Task.user_id == user.id)

    return query


def get_accessible_task(
    task_id: int,
    db: Session,
    user: User
) -> Task:
    task = db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Задача не найдена"
        )

    if not is_admin(user) and task.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Нет доступа к этой задаче"
        )

    return task


def recalculate_task(task: Task):
    task.is_urgent = calculate_urgency(task.deadline_at)
    task.quadrant = determine_quadrant(
        task.is_important,
        task.is_urgent
    )


@router.get("", response_model=List[TaskResponse])
def get_all_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = visible_tasks(current_user).order_by(Task.id)
    return db.scalars(query).all()


@router.get("/today", response_model=List[TaskResponse])
def get_tasks_today(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = visible_tasks(current_user).where(
        Task.deadline_at == date.today(),
        Task.completed.is_(False)
    ).order_by(Task.id)

    return db.scalars(query).all()


@router.get(
    "/quadrant/{quadrant}",
    response_model=List[TaskResponse]
)
def get_tasks_by_quadrant(
    quadrant: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if quadrant not in ("Q1", "Q2", "Q3", "Q4"):
        raise HTTPException(
            status_code=400,
            detail="Используйте Q1, Q2, Q3 или Q4"
        )

    query = visible_tasks(current_user).where(
        Task.quadrant == quadrant
    )

    return db.scalars(query).all()


@router.get(
    "/status/{task_status}",
    response_model=List[TaskResponse]
)
def get_tasks_by_status(
    task_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if task_status not in ("completed", "pending"):
        raise HTTPException(
            status_code=400,
            detail="Используйте completed или pending"
        )

    query = visible_tasks(current_user).where(
        Task.completed.is_(task_status == "completed")
    )

    return db.scalars(query).all()


@router.get("/search", response_model=List[TaskResponse])
def search_tasks(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    keyword = f"%{q.strip()}%"

    query = visible_tasks(current_user).where(
        or_(
            Task.title.ilike(keyword),
            Task.description.ilike(keyword)
        )
    )

    tasks = db.scalars(query).all()

    if not tasks:
        raise HTTPException(
            status_code=404,
            detail="Задачи не найдены"
        )

    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task_by_id(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_accessible_task(
        task_id,
        db,
        current_user
    )


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    urgency = calculate_urgency(task.deadline_at)

    new_task = Task(
        title=task.title,
        description=task.description,
        is_important=task.is_important,
        deadline_at=task.deadline_at,
        is_urgent=urgency,
        quadrant=determine_quadrant(
            task.is_important,
            urgency
        ),
        completed=False,
        user_id=current_user.id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = get_accessible_task(
        task_id,
        db,
        current_user
    )

    changes = task_update.model_dump(
        exclude_unset=True
    )

    for field, value in changes.items():
        setattr(task, field, value)

    if "completed" in changes:
        if task.completed and task.completed_at is None:
            task.completed_at = datetime.now()
        elif not task.completed:
            task.completed_at = None

    recalculate_task(task)

    db.commit()
    db.refresh(task)

    return task


@router.patch(
    "/{task_id}/complete",
    response_model=TaskResponse
)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = get_accessible_task(
        task_id,
        db,
        current_user
    )

    if not task.completed:
        task.completed = True
        task.completed_at = datetime.now()

    db.commit()
    db.refresh(task)

    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = get_accessible_task(
        task_id,
        db,
        current_user
    )

    db.delete(task)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
