from fastapi import APIRouter, Depends
from app.schemas.monitor import MonitorCreate, MonitorRead
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.monitor import Monitor
from typing import Annotated


router = APIRouter() 

# Returns 201 on successful creation
@router.post("/monitors", response_model = MonitorRead, status_code = 201)
def create_monitor(monitor_in: MonitorCreate, db:Annotated[Session, Depends(get_db)]):
    monitor = Monitor(
        name = monitor_in.name,
        url = str(monitor_in.url),
        check_interval_seconds = monitor_in.check_interval_seconds,
        expected_status_code = monitor_in.expected_status_code,
        is_enabled = monitor_in.is_enabled,
        timeout_seconds = monitor_in.timeout_seconds
    )
    db.add(monitor)
    db.commit()
    db.refresh(monitor)
    return monitor