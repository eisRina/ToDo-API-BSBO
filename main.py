
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import init_db, get_db
from models import Task
from routers import tasks, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Запуск приложения...")
    init_db()
    print("База данных готова к работе!")
    yield
    print("Остановка приложения...")


app = FastAPI(
    title="ToDo лист API",
    description="API для управления задачами с использованием матрицы Эйзенхауэра",
    version="2.0.0",
    contact={
        "name": "Ролдугина Ирина Олеговна"
    },
    lifespan=lifespan
)


# Подключение маршрутов API версии 2
app.include_router(tasks.router, prefix="/api/v2")
app.include_router(stats.router, prefix="/api/v2")


@app.get("/")
def welcome() -> dict:
    return {
        "title": app.title,
        "description": app.description,
        "version": app.version,
        "database": "PostgreSQL (Supabase)",
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
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status
    }
