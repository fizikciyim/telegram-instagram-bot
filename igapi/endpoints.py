from igapi.private_api import private


def get_user(username):
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"

    res = private.session.get(url)

    if res.status_code != 200:
        return None

    try:
        return res.json()["data"]["user"]
    except:
        return None
