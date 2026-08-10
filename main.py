import json
import time
import webbrowser

import requests
from dotenv import load_dotenv
import os


# =========================
# CONFIG
# =========================

CONFIG_FILE = "config.json"

TOKEN_URL = "https://id.kick.com/oauth/token"
API_URL = "https://api.kick.com/public/v1"


# =========================
# LOAD ENV
# =========================

load_dotenv()

CLIENT_ID = os.getenv("KICK_CLIENT_ID")
CLIENT_SECRET = os.getenv("KICK_CLIENT_SECRET")


if not CLIENT_ID or not CLIENT_SECRET:
    print("[ERROR] Client ID atau Client Secret belum diatur.")
    print()
    print("Buat file .env:")
    print("KICK_CLIENT_ID=CLIENT_ID_KAMU")
    print("KICK_CLIENT_SECRET=CLIENT_SECRET_KAMU")
    exit(1)


# =========================
# LOAD CONFIG
# =========================

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# =========================
# GET ACCESS TOKEN
# =========================

def get_access_token():

    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(
            TOKEN_URL,
            data=data,
            headers=headers,
            timeout=15
        )

        if response.status_code != 200:
            print(
                f"[ERROR] Token HTTP {response.status_code}: "
                f"{response.text}"
            )
            return None

        token_data = response.json()

        access_token = token_data.get("access_token")

        if not access_token:
            print("[ERROR] Access token tidak ditemukan.")
            return None

        print("[OK] KICK API access token berhasil diperoleh.")

        return access_token

    except requests.RequestException as error:
        print(f"[ERROR] Token request: {error}")
        return None


# =========================
# GET CHANNEL ID
# =========================

def get_channel_id(username, token):

    url = f"{API_URL}/channels"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    params = {
        "slug": username
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=15
        )

        if response.status_code != 200:
            print(
                f"[ERROR] {username}: "
                f"Channel HTTP {response.status_code}"
            )
            return None

        data = response.json()

        channels = data.get("data", [])

        if not channels:
            print(f"[NOT FOUND] {username}")
            return None

        channel = channels[0]

        return channel.get("broadcaster_user_id")

    except requests.RequestException as error:
        print(f"[ERROR] {username}: {error}")
        return None


# =========================
# CHECK LIVESTREAM
# =========================

def check_live(username, user_id, token):

    url = f"{API_URL}/livestreams"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    params = {
        "broadcaster_user_id": user_id
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=15
        )

        if response.status_code != 200:
            print(
                f"[ERROR] {username}: "
                f"Livestream HTTP {response.status_code}"
            )
            return False

        data = response.json()

        livestreams = data.get("data", [])

        return len(livestreams) > 0

    except requests.RequestException as error:
        print(f"[ERROR] {username}: {error}")
        return False


# =========================
# OPEN STREAM
# =========================

def open_stream(username):

    url = f"https://kick.com/{username}"

    print(f"[OPEN] {url}")

    webbrowser.open_new_tab(url)


# =========================
# MAIN
# =========================

def main():

    config = load_config()

    channels = config.get("channels", [])
    interval = config.get("check_interval", 60)

    if not channels:
        print("[ERROR] Tidak ada channel di config.json")
        return

    print("=" * 55)
    print("             KICK AUTO STREAM")
    print("=" * 55)

    print(f"Channel : {len(channels)}")
    print(f"Interval: {interval} detik")

    print("=" * 55)

    # Get API token
    token = get_access_token()

    if not token:
        return

    print()
    print("[INFO] Mengambil ID channel...")

    # Resolve channel IDs
    channel_ids = {}

    for channel in channels:

        channel = channel.strip()

        if not channel:
            continue

        user_id = get_channel_id(channel, token)

        if user_id:
            channel_ids[channel.lower()] = user_id

            print(
                f"[OK] {channel} "
                f"-> ID {user_id}"
            )

        else:
            print(
                f"[FAIL] Tidak dapat menemukan "
                f"channel {channel}"
            )

    print()
    print("=" * 55)
    print("Mulai monitoring...")
    print("=" * 55)

    # Previous status
    previous_status = {
        channel: False
        for channel in channel_ids
    }

    while True:

        for channel, user_id in channel_ids.items():

            live = check_live(
                channel,
                user_id,
                token
            )

            if live:

                print(f"[LIVE] {channel}")

                # Open only when OFFLINE -> LIVE
                if not previous_status[channel]:

                    open_stream(channel)

            else:

                print(f"[OFFLINE] {channel}")

            previous_status[channel] = live

        print("-" * 55)
        print(
            f"Menunggu {interval} detik..."
        )
        print("-" * 55)

        time.sleep(interval)


if __name__ == "__main__":
    main()
