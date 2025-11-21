import time

CACHE = {}

# ---------------------------
#  Cache'ten veri alma
# ---------------------------
def get_cache(key):
    data = CACHE.get(key)

    if not data:
        return None

    # Süre dolmuşsa sil
    if data["expires_at"] < time.time():
        del CACHE[key]
        return None

    return data["value"]


# ---------------------------
#  Cache'e veri yazma
# ---------------------------
def set_cache(key, value, ttl=60):
    CACHE[key] = {
        "value": value,
        "expires_at": time.time() + ttl  # 60 saniye
    }
