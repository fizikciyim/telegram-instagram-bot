import os
import requests
from igapi.private_api import private
from cache import get_cache, set_cache


def download_url(url, filename):
    """URL'den dosya indirir (dosya varsa tekrar indirmez)"""
    os.makedirs("downloads", exist_ok=True)
    path = f"downloads/{filename}"

    # Eğer dosya daha önce indiyse → tekrar indirme
    if os.path.exists(path):
        return path

    headers = {
        "User-Agent": private.session.headers.get("User-Agent", "Instagram 300.0.0.0.30 Android")
    }

    data = requests.get(url, headers=headers).content

    with open(path, "wb") as f:
        f.write(data)

    return path


def download_story(user_id):
    """Hikayeleri indirir (cache + dosya cache destekli)"""

    # 1) Bellek cache kontrolü
    cache_key = f"story_files:{user_id}"
    cached = get_cache(cache_key)
    if cached:
        return cached   # ✔ Dosyalar zaten indirilmiş

    # 2) API’den hikayeleri çek
    items = private.user_stories(user_id)
    if not items:
        return []

    result = []

    for item in items:

        # Fotoğraf
        if item.get("media_type") == 1:
            media_url = item["image_versions2"]["candidates"][0]["url"]
            ext = "jpg"

        # Video
        elif item.get("media_type") == 2:
            media_url = item["video_versions"][0]["url"]
            ext = "mp4"

        else:
            continue

        filename = f"story_{item['id']}.{ext}"
        path = download_url(media_url, filename)
        result.append(path)

    # 3) Belleğe kaydet (60 saniye)
    set_cache(cache_key, result)

    return result



def download_highlights(user_id):
    """Öne çıkanları indirir (dosya cache var fakat API cache yok şu an)"""

    url = f"https://i.instagram.com/api/v1/highlights/{user_id}/highlights_tray/"
    res = private.session.get(url)

    if res.status_code != 200:
        return []

    trays = res.json().get("tray", [])
    result = []

    for tray in trays:
        for item in tray.get("items", []):
            media_url = private.media_url(item)
            if not media_url:
                continue

            ext = "mp4" if "video" in media_url else "jpg"
            filename = f"hl_{item['id']}.{ext}"

            path = download_url(media_url, filename)
            result.append(path)

    return result



def get_story_thumbnails(user_id):
    """Story thumbnail URL'leri"""
    items = private.user_stories(user_id)
    if not items:
        return []
    thumbnails = []

    for item in items:
        try:
            thumb = item["image_versions2"]["candidates"][2]["url"]
        except:
            thumb = item["image_versions2"]["candidates"][0]["url"]

        thumbnails.append({
            "id": item["id"],
            "thumbnail": thumb
        })

    return thumbnails



def download_single_story(story_id):
    url = f"https://i.instagram.com/api/v1/media/{story_id}/info/"
    res = private.session.get(url)

    if res.status_code != 200:
        return None

    try:
        item = res.json()["items"][0]
    except:
        return None

    # Fotoğraf
    if item.get("media_type") == 1:
        media_url = item["image_versions2"]["candidates"][0]["url"]
        ext = "jpg"

    # Video
    elif item.get("media_type") == 2:
        media_url = item["video_versions"][0]["url"]
        ext = "mp4"
    else:
        return None

    filename = f"story_{story_id}.{ext}"
    return download_url(media_url, filename)
