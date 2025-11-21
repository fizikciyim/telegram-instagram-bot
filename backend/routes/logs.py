from fastapi import APIRouter
from services.users import upsert_user
from services.logs import add_log

router = APIRouter()

@router.post("/log")
def log_route(data: dict):
    user_id = data.get("user_id")
    action = data.get("action")
    extra = str(data.get("extra"))

    ok = add_log(user_id, action, extra)
    return {"success": ok}
