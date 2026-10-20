from typing import Annotated

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.db.session import get_db
from fastapi.responses import JSONResponse

app = FastAPI() # initializer to FastAPI

@app.get("/health") # Create slug to run health check
def health_check():
    return {
        "status": "healthy",
        "service": "BeaconKeep"
    }

@app.get("/health/db") # Create health db check
def db_health_check(db:Annotated[Session, Depends(get_db)]):
    statement = text("SELECT 1")
    try:
        db.execute(statement)
        return{
        "status": "healthy",
        "database": "connected"
        }
    except OperationalError:
        return JSONResponse(content = {
            "status": "unhealthy",
            "database": "disconnected"
        }, status_code = 503)
        
        