# Creates and manages database sessions used to interact with the database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
