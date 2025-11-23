# backend/premium.py

from db import get_connection
from mysql.connector import Error
from datetime import datetime, timedelta


def add_premium(user_id: int, days: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET is_premium = 1,
                premium_until = IF(
                    premium_until IS NULL OR premium_until < NOW(),
                    DATE_ADD(NOW(), INTERVAL %s DAY),
                    DATE_ADD(premium_until, INTERVAL %s DAY)
                )
            WHERE id = %s
        """, (days, days, user_id))

        conn.commit()
        cursor.close()
        conn.close()

        print(f"💎 Premium {days} gün verildi → {user_id}")
        return True

    except Error as e:
        print("❌ Premium hatası:", e)
        return False


def is_premium(user_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT is_premium, premium_until
            FROM users
            WHERE id = %s
        """, (user_id,))

        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            return False

        if user["premium_until"] and user["premium_until"] > datetime.now():
            return True
        return False

    except Error as e:
        print("❌ Premium kontrol hatası:", e)
        return False
