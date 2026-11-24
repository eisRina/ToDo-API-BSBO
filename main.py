
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import init_db, get_db
from routers import tasks, stats
from scheduler import start_scheduler, update_task_urgency


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Запуск приложения...")

    # Инициализация PostgreSQL
    init_db()
    print("База данных инициализирована!")

    # Пересчёт при запуске
    update_task_urgency()

    # Запуск ежедневного расписания
    scheduler = start_scheduler()

    print("Приложение готово к работе!")

    try:
        yield
    finally:
        scheduler.shutdown(wait=False)
        print("Планировщик остановлен")
        print("Остановка приложения...")


app = FastAPI(
    title="ToDo лист API",
    description=(
        "API для управления задачами с использованием "
        "матрицы Эйзенхауэра и автоматического учёта дедлайнов"
    ),
    version="2.1.0",
    contact={
        "name": "Ролдугина Ирина Олеговна"
    },
    lifespan=lifespan
)


app.include_router(tasks.router, prefix="/api/v2")
app.include_router(stats.router, prefix="/api/v2")


@app.get("/")
def welcome() -> dict:
    return {
        "title": app.title,
        "description": app.description,
        "version": app.version,
        "database": "PostgreSQL (Supabase)",
        "scheduler": "APScheduler",
        "docs": "/docs"
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)) -> dict:
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": (
            "healthy" if db_status == "connected"
            else "unhealthy"
        ),
        "database": db_status
    }
