from typing import Annotated

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db

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
    db.execute(statement)
    return{
        "status": "healthy",
        "database": "connected"
    }

async def override_get_db(q : str | None = None):
    return {"status": "unhealthy", "database": "disconnected"}

app.dependency_overrides[get_db] = override_get_db