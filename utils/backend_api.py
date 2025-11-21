import httpx
from config import BACKEND_URL

async def check_limit(telegram_id):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BACKEND_URL}/check_limit",
            json={"telegram_id": telegram_id}
        )
        return resp.json()
    
# Kullanıcı verilerini (ve PREMIUM durumunu) çekme
async def get_user_data(telegram_id):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BACKEND_URL}/user/{telegram_id}")
        if resp.status_code == 200:
            return resp.json()
        return {}