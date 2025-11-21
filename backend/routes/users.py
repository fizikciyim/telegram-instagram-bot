from fastapi import APIRouter, HTTPException
from services.users import upsert_user, get_user
from db import get_db
from datetime import datetime

router = APIRouter()

@router.post("/register")
def register(data: dict):
    telegram_id = data.get("telegram_id")
    username = data.get("username", "")

    ok = upsert_user(telegram_id, username)
    
    return {"success": ok}


@router.get("/user/{telegram_id}")
def user_info(telegram_id: int):
    user = get_user(telegram_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Premium bitmişse otomatik sıfırla
    is_premium = 0
    premium_until = user.get("premium_until")

    if premium_until:
        if premium_until > datetime.now():
            is_premium = 1
        else:
            is_premium = 0  # süresi geçmiş
            premium_until = None

    return {
        "telegram_id": user["id"],
        "username": user["username"],
        "daily_limit": user.get("daily_limit", 20),
        "used_today": user.get("used_today", 0),
        "is_premium": is_premium,
        "premium_until": premium_until
    }