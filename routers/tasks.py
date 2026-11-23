
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from database import get_db
from models import Task
from schemas import TaskCreate, TaskUpdate, TaskResponse


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Task not found"}}
)


# Автоматический расчет срочности
def calculate_urgency(deadline_at: date) -> bool:
    days_left = (deadline_at - date.today()).days
    return days_left <= 3


# Определение квадранта
def calculate_quadrant(is_important: bool, is_urgent: bool) -> str:
    if is_important and is_urgent:
        return "Q1"
    if is_important:
        return "Q2"
    if is_urgent:
        return "Q3"
    return "Q4"


# Пересчет срочности и квадранта
def update_deadline_logic(task: Task):
    if task.deadline_at is not None:
        task.is_urgent = calculate_urgency(task.deadline_at)

    task.quadrant = calculate_quadrant(
        task.is_important,
        task.is_urgent
    )


# Получить все задачи
@router.get("", response_model=List[TaskResponse])
def get_all_tasks(db: Session = Depends(get_db)):
    return db.scalars(
        select(Task).order_by(Task.id)
    ).all()


# Получить задачи по квадранту
@router.get("/quadrant/{quadrant}", response_model=List[TaskResponse])
def get_tasks_by_quadrant(
    quadrant: str,
    db: Session = Depends(get_db)
):
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]:
        raise HTTPException(
            status_code=400,
            detail="Используйте Q1, Q2, Q3 или Q4"
        )

    return db.scalars(
        select(Task).where(Task.quadrant == quadrant)
    ).all()


# Получить задачи по статусу
@router.get("/status/{task_status}", response_model=List[TaskResponse])
def get_tasks_by_status(
    task_status: str,
    db: Session = Depends(get_db)
):
    if task_status not in ["completed", "pending"]:
        raise HTTPException(
            status_code=404,
            detail="Используйте completed или pending"
        )

    return db.scalars(
        select(Task).where(
            Task.completed == (task_status == "completed")
        )
    ).all()


# Поиск задач
@router.get("/search", response_model=List[TaskResponse])
def search_tasks(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db)
):
    keyword = f"%{q.strip()}%"

    tasks = db.scalars(
        select(Task).where(
            or_(
                Task.title.ilike(keyword),
                Task.description.ilike(keyword)
            )
        )
    ).all()

    if not tasks:
        raise HTTPException(
            status_code=404,
            detail="Задачи не найдены"
        )

    return tasks


# Получить задачу по ID
@router.get("/{task_id}", response_model=TaskResponse)
def get_task_by_id(
    task_id: int,
    db: Session = Depends(get_db)
):
    task = db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Задача не найдена"
        )

    return task


# Создать задачу с дедлайном
@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db)
):
    is_urgent = calculate_urgency(task.deadline_at)

    new_task = Task(
        title=task.title,
        description=task.description,
        is_important=task.is_important,
        deadline_at=task.deadline_at,
        is_urgent=is_urgent,
        quadrant=calculate_quadrant(
            task.is_important,
            is_urgent
        ),
        completed=False
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


# Обновить задачу
@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
):
    task = db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Задача не найдена"
        )

    update_data = task_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(task, field, value)

    update_deadline_logic(task)

    db.commit()
    db.refresh(task)

    return task


# Завершить задачу
@router.patch("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    task = db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Задача не найдена"
        )

    task.completed = True

    db.commit()
    db.refresh(task)

    return task


# Удалить задачу
@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    task = db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Задача не найдена"
        )

    db.delete(task)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
