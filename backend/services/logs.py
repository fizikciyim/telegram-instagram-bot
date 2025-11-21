# backend/logs.py

from db import get_connection
from mysql.connector import Error


def add_log(user_id: int, action: str, extra: str = None):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO logs (user_id, action, extra)
            VALUES (%s, %s, %s)
        """, (user_id, action, extra))

        conn.commit()
        cursor.close()
        conn.close()

        print(f"📘 Log kaydedildi: {action}")
        return True

    except Error as e:
        print("❌ Log hatası:", e)
        return False
