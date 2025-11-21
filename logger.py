import os
from datetime import datetime

LOG_FILE = "logs/bot.log"

# logs klasörü yoksa oluştur
os.makedirs("logs", exist_ok=True)


def log(text: str):
    """Bot için log kaydı ekler"""
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{time}] {text}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)

    print(entry, end="")  # konsola da yaz (debug için)
