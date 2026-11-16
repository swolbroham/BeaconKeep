from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.monitor import MonitorCreate, MonitorRead
from app.db.session import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
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

@router.get("/monitors", response_model = list[MonitorRead])
def read_monitors(
    db:Annotated[Session, Depends(get_db)],
    offset: int = Query(default = 0, ge=0),
    limit: int = Query(default=10, ge=1, le=100)
    ):
    monitors = db.scalars(select(Monitor)
                         .order_by(Monitor.id)
                         .limit(limit)
                         .offset(offset)).all()
    
    return monitors

@router.get("/monitors/{monitor_id}", response_model = MonitorRead)
def read_monitor(monitor_id : int,  db:Annotated[Session, Depends(get_db)]):
    monitor = db.get(Monitor, monitor_id)
    if monitor is None: 
        raise HTTPException(404, detail = "Monitor not found")
    return monitor
