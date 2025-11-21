from fastapi import APIRouter
from services.users import upsert_user

router = APIRouter()

@router.get("/premium/check/{uid}")
def check(uid: int):
    return {"premium": is_premium(uid)}

@router.post("/premium/add")
def add_route(data: dict):
    user_id = data.get("user_id")
    days = data.get("days", 30)

    ok = add_premium(user_id, days)
    return {"success": ok}
