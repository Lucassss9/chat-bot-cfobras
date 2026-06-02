import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

url_database = os.getenv("DATABASE_URL")
engine = create_engine(url_database)

session_local = sessionmaker( bind=engine, autocommit=False, autoflush=False)
base = declarative_base()
