from fastapi import APIRouter
from sqlalchemy import text

from src.app.db.session import engine

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
def health_check():
    return {"status": "ok"}


@router.get("/db")
def test_db_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "Database connected"}
    except Exception as e:
        return {"error": str(e)}
