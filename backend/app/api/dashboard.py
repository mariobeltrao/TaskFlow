from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.task_repository import TaskRepository
from app.schemas.task import DashboardSummary, TaskResponse
from app.services.task_service import TaskService

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db), _user: User = Depends(current_user)):
    return TaskService(db).summary()


@router.get("/calendar", response_model=list[TaskResponse])
def calendar(month: str, db: Session = Depends(get_db), _user: User = Depends(current_user)):
    year, month_number = map(int, month.split("-"))
    start = date(year, month_number, 1)
    end = date(year + (month_number == 12), month_number % 12 + 1, 1)
    items, _ = TaskRepository(db).list(
        date_from=start, date_to=date.fromordinal(end.toordinal() - 1), page_size=100
    )
    return items
