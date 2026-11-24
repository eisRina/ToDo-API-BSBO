
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import init_db, get_db
from routers import tasks, stats, auth, admin
from scheduler import start_scheduler, update_task_urgency

# Регистрируем все модели до инициализации БД
import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Запуск приложения...")

    init_db()
    print("База данных инициализирована!")

    update_task_urgency()
    scheduler = start_scheduler()

    print("Приложение готово к работе!")

    try:
        yield
    finally:
        scheduler.shutdown(wait=False)
        print("Планировщик остановлен")


app = FastAPI(
    title="ToDo лист API",
    description=(
        "Многопользовательское API управления задачами "
        "с JWT-аутентификацией, PostgreSQL и APScheduler"
    ),
    version="3.0.0",
    contact={
        "name": "Ролдугина Ирина Олеговна"
    },
    lifespan=lifespan
)


app.include_router(auth.router, prefix="/api/v2")
app.include_router(admin.router, prefix="/api/v2")
app.include_router(tasks.router, prefix="/api/v2")
app.include_router(stats.router, prefix="/api/v2")


@app.get("/")
def welcome():
    return {
        "title": app.title,
        "description": app.description,
        "version": app.version,
        "database": "PostgreSQL (Supabase)",
        "authentication": "JWT",
        "scheduler": "APScheduler",
        "docs": "/docs"
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception:
        return {
            "status": "unhealthy",
            "database": "disconnected"
        }
