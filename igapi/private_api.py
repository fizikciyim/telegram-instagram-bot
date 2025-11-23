import requests
from config import COOKIES
from cache import get_cache, set_cache


class PrivateAPI:
    def __init__(self):
        self.session = requests.Session()

        self.user_agent = (
            "Instagram 295.0.0.34.109 Android (30/11; 420dpi; 1080x1920; "
            "Google; Pixel 5; redfin; redfin; en_US; 456096598)"
        )

        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "*/*",
            "Connection": "keep-alive",
            "X-CSRFToken": COOKIES.get("csrftoken", ""),
            "Referer": "https://www.instagram.com/",
        })

        for k, v in COOKIES.items():
            self.session.cookies.set(k, v, domain=".instagram.com")

        print("Instagram Cookie Login → Başarılı!")

    def user_info_by_username(self, username: str):
        key = f"profile:{username}"

        cached = get_cache(key)
        if cached:
            return cached

        url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
        res = self.session.get(url)

        if res.status_code != 200:
            return None

        try:
            data = res.json()["data"]["user"]

            set_cache(key, data)  
            return data

        except:
            return None

    def user_stories(self, user_id: int):
        key = f"stories:{user_id}"

        cached = get_cache(key)
        if cached:
            return cached

        url = f"https://i.instagram.com/api/v1/feed/user/{user_id}/story/"
        res = self.session.get(url)

        if res.status_code != 200:
            return []

        data = res.json()

        if not data:
            return []

        reel = data.get("reel")
        if not reel:
            return []

        items = reel.get("items", [])
        if not items:
            return []

        set_cache(key, items)
        return items

    def user_highlights(self, user_id: int):
        url = f"https://i.instagram.com/api/v1/highlights/{user_id}/highlights_tray/"
        res = self.session.get(url)

        if res.status_code != 200:
            return []

        return res.json().get("tray", [])
    
    def highlight_items(self, hid):
        url = f"https://i.instagram.com/api/v1/feed/reels_media/?reel_ids={hid}"
        res = self.session.get(url)

        if res.status_code != 200:
            return []

        reels = res.json().get("reels", {})
        return reels.get(str(hid), {}).get("items", [])

    def user_posts(self, user_id, max_id=None, amount=10):
        # max_id None ise boş string yapalım → split hatası çıkmaz
        key_max = max_id if max_id is not None else "start"
        key = f"posts:{user_id}:{key_max}"

        cached = get_cache(key)
        if cached:
            return cached
        url = f"https://i.instagram.com/api/v1/feed/user/{user_id}/"
        if max_id:
            url += f"?max_id={max_id}"

        res = self.session.get(url)
        if res.status_code != 200:
            return {"posts": [], "next": None}

        data = res.json()

        items = data.get("items", [])
        next_max_id = data.get("next_max_id")

        items = items[:amount]

        result = {
            "posts": items,
            "next": next_max_id
        }

        set_cache(key, result, ttl=300)

        return result


    def user_reels(self, user_id, amount=12):
        url = f"https://i.instagram.com/api/v1/clips/user/{user_id}/?count={amount}"
        res = self.session.get(url)

        if res.status_code != 200:
            return []

        return res.json().get("items", [])

    def media_url(self, item):
        if "video_versions" in item:
            return item["video_versions"][0]["url"]

        if "image_versions2" in item:
            return item["image_versions2"]["candidates"][0]["url"]

        return None

    def post_media(self, media):
        result = []

        if "carousel_media" in media:
            for item in media["carousel_media"]:
                media_type = "video" if "video_versions" in item else "photo"
                result.append({"url": self.media_url(item), "type": media_type})
        else:
            media_type = "video" if "video_versions" in media else "photo"
            result.append({"url": self.media_url(media), "type": media_type})

        return result

    def post_thumbnail(self, media):
        if "image_versions2" in media:
            return media["image_versions2"]["candidates"][0]["url"]

        if "carousel_media" in media:
            first = media["carousel_media"][0]
            return first["image_versions2"]["candidates"][0]["url"]

        return None

    def reel_url(self, item):
        if "video_versions" in item:
            return item["video_versions"][0]["url"]
        return None
    
    def user_highlights_full(self, user_id: int):
        url = f"https://i.instagram.com/api/v1/highlights/{user_id}/highlights_tray/"
        res = self.session.get(url)

        if res.status_code != 200:
            return []

        return res.json().get("tray", [])


private = PrivateAPI()
