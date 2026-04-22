# Creates and manages database sessions used to interact with the database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app.core.config import settings

database_url = settings.DATABASE_URL

# Disable prepared statements if using Supabase pooler
connect_args = {}
if "pooler.supabase.com" in database_url or ":6543/" in database_url:
    connect_args["prepare_threshold"] = None

engine = create_engine(
    database_url,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
