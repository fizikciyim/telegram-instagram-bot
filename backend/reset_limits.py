from db import get_connection
from datetime import date

def reset_all_limits():
    conn = get_connection()
    cursor = conn.cursor()

    today = date.today()

    cursor.execute("""
        UPDATE users
        SET used_today = 0,
            last_reset = %s
    """, (today,))

    conn.commit()
    cursor.close()
    conn.close()

    print("✔ Tüm kullanıcıların günlük hakkı sıfırlandı.")

if __name__ == "__main__":
    reset_all_limits()
