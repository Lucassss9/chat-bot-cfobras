import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

load_dotenv()

Base = declarative_base()

engine = create_engine(os.getenv('DATABASE_URL'), pool_pre_ping=True)
session_local = sessionmaker( bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = session_local()

    try:
        yield db
    finally:
        db.close()