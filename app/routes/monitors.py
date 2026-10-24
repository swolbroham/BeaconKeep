from fastapi import APIRouter, Depends
from app.schemas.monitor import MonitorCreate
from app.db.session import get_db
from sqlalchemy.orm import Session
from typing import Annotated


router = APIRouter() 

@router.post("/monitors")
def create_monitor(monitor_in: MonitorCreate, db:Annotated[Session, Depends(get_db)]):
    return MonitorCreate