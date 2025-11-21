from fastapi import APIRouter
from services.limits import check_and_update_limit

router = APIRouter()

@router.post("/check_limit")
def check_limit(data: dict):
    # Hem telegram_id hem user_id destekle
    user_id = data.get("user_id") or data.get("telegram_id")

    result = check_and_update_limit(user_id)
    return result