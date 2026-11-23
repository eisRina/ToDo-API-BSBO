
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


def calculate_quadrant(is_important: bool, is_urgent: bool) -> str:
    if is_important and is_urgent:
        return "Q1"
    if is_important:
        return "Q2"
    if is_urgent:
        return "Q3"
    return "Q4"


# Получить все задачи
@router.get("", response_model=List[TaskResponse])
def get_all_tasks(db: Session = Depends(get_db)):
    return db.scalars(select(Task).order_by(Task.id)).all()


# Фильтрация по квадранту
@router.get("/quadrant/{quadrant}", response_model=List[TaskResponse])
def get_tasks_by_quadrant(
    quadrant: str,
    db: Session = Depends(get_db)
):
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]:
        raise HTTPException(
            status_code=400,
            detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4"
        )

    return db.scalars(
        select(Task).where(Task.quadrant == quadrant)
    ).all()


# Фильтрация по статусу
@router.get("/status/{task_status}", response_model=List[TaskResponse])
def get_tasks_by_status(
    task_status: str,
    db: Session = Depends(get_db)
):
    if task_status not in ["completed", "pending"]:
        raise HTTPException(
            status_code=404,
            detail="Статус не найден. Используйте: completed или pending"
        )

    is_completed = task_status == "completed"

    return db.scalars(
        select(Task).where(Task.completed == is_completed)
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
            detail="Задачи по вашему запросу не найдены"
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


# Создать новую задачу
@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db)
):
    new_task = Task(
        title=task.title,
        description=task.description,
        is_important=task.is_important,
        is_urgent=task.is_urgent,
        quadrant=calculate_quadrant(
            task.is_important,
            task.is_urgent
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

    if "is_important" in update_data or "is_urgent" in update_data:
        task.quadrant = calculate_quadrant(
            task.is_important,
            task.is_urgent
        )

    db.commit()
    db.refresh(task)

    return task


# Отметить задачу выполненной
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

    return Response(status_code=status.HTTP_204_NO_CONTENT)
