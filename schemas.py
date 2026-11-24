
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, computed_field


class TaskBase(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Название задачи"
    )

    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Описание задачи"
    )

    is_important: bool = Field(
        ...,
        description="Важность задачи"
    )


class TaskCreate(TaskBase):
    deadline_at: Optional[date] = Field(
        None,
        description="Плановая дата выполнения задачи"
    )


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100
    )

    description: Optional[str] = Field(
        None,
        max_length=500
    )

    is_important: Optional[bool] = None
    deadline_at: Optional[date] = None
    completed: Optional[bool] = None


class TaskResponse(TaskBase):
    id: int
    is_urgent: bool
    quadrant: str
    completed: bool

    created_at: datetime
    deadline_at: Optional[date] = None
    completed_at: Optional[datetime] = None

    @computed_field
    @property
    def days_until_deadline(self) -> Optional[int]:
        if self.deadline_at is None:
            return None

        return (self.deadline_at - date.today()).days

    @computed_field
    @property
    def status_message(self) -> str:
        if self.completed:
            if self.deadline_at is None or self.completed_at is None:
                return "Задача выполнена"

            if self.completed_at.date() <= self.deadline_at:
                return "Завершена в срок"

            return "Завершена с опозданием"

        if self.deadline_at is None:
            return "Дедлайн не установлен"

        if self.days_until_deadline < 0:
            return "Задача просрочена"

        if self.days_until_deadline <= 3:
            return "Срок выполнения приближается"

        return "Выполняется по плану"

    model_config = {"from_attributes": True}


class TimingStatsResponse(BaseModel):
    completed_on_time: int = Field(
        description="Количество задач, завершённых в срок"
    )

    completed_late: int = Field(
        description="Количество задач, завершённых с опозданием"
    )

    on_plan_pending: int = Field(
        description="Количество невыполненных задач в пределах срока"
    )

    overtime_pending: int = Field(
        description="Количество просроченных невыполненных задач"
    )
