import base64
import json
import urllib.parse as urlparse
from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from services.premium import add_premium, is_premium
from services.telegram_notifier import send_premium_message

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


@router.post("/shopier/webhook")
async def shopier_webhook(request: Request):
    form = await request.form()
    print("RAW FORM:", form)

    res_b64 = form.get("res")
    if not res_b64:
        return PlainTextResponse("success")

    decoded = base64.b64decode(res_b64).decode("utf-8")
    data = json.loads(decoded)

    print("DECODED JSON:", data)

    product_id = int(data.get("productid"))

    # ⭐⭐⭐ SİPARİŞ NOTU → UID ⭐⭐⭐
    uid = data.get("customernote", "").strip()

    if not uid:
        print("❌ Sipariş notu boş, UID bulunamadı.")
        return PlainTextResponse("success")

    # UID geçerli mi?
    if not uid.isdigit():
        print("❌ UID rakam değil:", uid)
        return PlainTextResponse("success")

    telegram_id = int(uid)

    # --- PREMIUM VER ---
    if product_id == 41409641:
        add_premium(telegram_id, 1)
        await send_premium_message(
            telegram_id,
            "🎉 *1 Günlük Premium aktif edildi!*\n\nArtık botu sınırsız kullanabilirsin. 💎"
        )

    elif product_id == 41409673:
        add_premium(telegram_id, 30)
        await send_premium_message(
            telegram_id,
            "🎉 *30 Günlük Premium aktif edildi!*\n\nArtık botu sınırsız kullanabilirsin. 💎"
        )

    return PlainTextResponse("success")