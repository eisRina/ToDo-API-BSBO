
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import select

from database import SessionLocal
from models import Task
from utils import calculate_urgency, determine_quadrant


def update_task_urgency():
    print(f"[{datetime.now()}] Автоматический пересчёт срочности...")

    with SessionLocal() as db:
        try:
            tasks = db.scalars(
                select(Task).where(Task.completed.is_(False))
            ).all()

            updated_count = 0

            for task in tasks:
                # Старые задачи без дедлайна не изменяем
                if task.deadline_at is None:
                    continue

                new_urgency = calculate_urgency(task.deadline_at)
                new_quadrant = determine_quadrant(
                    task.is_important,
                    new_urgency
                )

                if (
                    task.is_urgent != new_urgency
                    or task.quadrant != new_quadrant
                ):
                    task.is_urgent = new_urgency
                    task.quadrant = new_quadrant
                    updated_count += 1

            db.commit()

            print(
                f"Пересчёт завершён. "
                f"Проверено: {len(tasks)}. "
                f"Обновлено: {updated_count}."
            )

        except Exception as error:
            db.rollback()
            print(f"Ошибка пересчёта: {error}")
            raise


def start_scheduler():
    scheduler = BackgroundScheduler()

    # Основное расписание: ежедневно в 09:00
    scheduler.add_job(
        update_task_urgency,
        trigger="cron",
        hour=9,
        minute=0,
        id="update_task_urgency",
        name="Ежедневный пересчёт срочности",
        replace_existing=True,
        max_instances=1
    )

    scheduler.start()

    print("Планировщик запущен: ежедневно в 09:00")

    return scheduler
