# backend/users.py

from db import get_connection
from mysql.connector import Error


def upsert_user(user_id: int, username: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (id, username)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE username = %s
        """, (user_id, username, username))

        conn.commit()
        cursor.close()
        conn.close()

        print(f"✔ Kullanıcı kaydedildi: {user_id}")
        return True

    except Error as e:
        print("❌ Kullanıcı kayıt hatası:", e)
        return False


def get_user(user_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()
        return user

    except Error as e:
        print("❌ Kullanıcı getirme hatası:", e)
        return None
