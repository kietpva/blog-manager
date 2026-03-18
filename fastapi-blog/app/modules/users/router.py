from fastapi import APIRouter
from app.dependencies.rbac import Admin, Authenticated

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", dependencies=[Authenticated])
def get_me():
    return {"data": "user"}


@router.get("/", dependencies=[Admin])
def get_users():
    return {"data": "Only admin can see this"}
