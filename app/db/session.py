import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

db_url = os.environ["DATABASE_URL"]

engine = create_engine(db_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind= engine, autoflush=False)

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()


