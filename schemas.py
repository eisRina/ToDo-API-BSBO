
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
    deadline_at: date = Field(
        ...,
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
    completed: Optional[bool] = None
    deadline_at: Optional[date] = None


class TaskResponse(TaskBase):
    id: int

    is_urgent: bool = Field(
        description="Автоматически рассчитанная срочность"
    )

    quadrant: str
    completed: bool
    created_at: datetime
    deadline_at: Optional[date] = None

    @computed_field
    @property
    def days_until_deadline(self) -> Optional[int]:
        if self.deadline_at is None:
            return None

        return (self.deadline_at - date.today()).days

    model_config = {"from_attributes": True}
