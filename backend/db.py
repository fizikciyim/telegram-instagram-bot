# backend/db.py

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# .env dosyasını yükle
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")


# -----------------------
#  MySQL bağlantısı
# -----------------------
def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )

def get_db():
    return get_connection()

# -----------------------
#  Veritabanı oluşturma
# -----------------------
def create_database():
    try:
        # database=DB_NAME yazmıyoruz çünkü DB yok
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        conn.commit()

        cursor.close()
        conn.close()
        print(f"✔ Veritabanı oluşturuldu (veya zaten vardı): {DB_NAME}")

    except Error as e:
        print("❌ DB Hatası:", e)


# -----------------------
#  Tabloları oluşturma
# -----------------------
def create_tables():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY,
                username VARCHAR(255),
                is_premium BOOLEAN DEFAULT 0,
                premium_until DATETIME NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT,
                action VARCHAR(255),
                extra TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        cursor.close()
        conn.close()

        print("✔ Tablolar oluşturuldu (veya zaten vardı).")

    except Error as e:
        print("❌ Tablo Hatası:", e)
