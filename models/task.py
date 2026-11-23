
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text
from sqlalchemy.sql import func

from database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    is_important = Column(Boolean, nullable=False, default=False)

    # Срочность теперь рассчитывается по дедлайну.
    # Столбец сохраняем для совместимости с PostgreSQL.
    is_urgent = Column(Boolean, nullable=False, default=False)

    quadrant = Column(String(2), nullable=False)
    completed = Column(Boolean, nullable=False, default=False)

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    deadline_at = Column(Date, nullable=True)

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}')>"
