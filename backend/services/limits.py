from datetime import date, datetime
from db import get_db  # veya sende hangisi varsa

def check_and_update_limit(user_id: int):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        conn.close()
        return {"allowed": False, "reason": "user_not_found"}

    today = date.today()

    # ========== PREMIUM KONTROLÜ ==========
    is_premium = bool(user.get("is_premium"))
    premium_until = user.get("premium_until")

    if is_premium and premium_until:
        # premium_until datetime ise sadece tarihi al
        if isinstance(premium_until, datetime):
            premium_date = premium_until.date()
        else:
            premium_date = premium_until

        if premium_date >= today:
            cursor.close()
            conn.close()
            return {
                "allowed": True,
                "reason": "premium",
                "daily_limit": user.get("daily_limit", 999999),
                "used_today": user.get("used_today", 0),
            }

    # ========== NORMAL KULLANICI KONTROLÜ ==========
    daily_limit = int(user.get("daily_limit", 20))
    used_today = int(user.get("used_today", 0))
    last_usage_date = user.get("last_usage_date")

    # gün değişmişse sıfırla
    if last_usage_date is None or (
        isinstance(last_usage_date, datetime) and last_usage_date.date() != today
    ) or (
        isinstance(last_usage_date, date) and last_usage_date != today
    ):
        used_today = 0

    # limit doldu mu?
    if used_today >= daily_limit:
        cursor.close()
        conn.close()
        return {
            "allowed": False,
            "reason": "limit",
            "daily_limit": daily_limit,
            "used_today": used_today,
        }

    # limiti 1 artır
    used_today += 1
    cursor.execute(
        "UPDATE users SET used_today = %s, last_usage_date = %s WHERE id = %s",
        (used_today, today, user_id),
    )
    conn.commit()

    cursor.close()
    conn.close()

    return {
        "allowed": True,
        "reason": "normal",
        "daily_limit": daily_limit,
        "used_today": used_today,
    }
