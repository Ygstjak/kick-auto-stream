import json
import time
import webbrowser
import requests

CONFIG_FILE = "config.json"


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def check_live(username):
    url = f"https://kick.com/api/v1/channels/{username}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        if response.status_code != 200:
            print(
                f"[ERROR] {username}: "
                f"HTTP {response.status_code}"
            )
            return False

        data = response.json()

        return data.get("livestream") is not None

    except requests.RequestException as error:
        print(f"[ERROR] {username}: {error}")
        return False


def open_stream(username):
    url = f"https://kick.com/{username}"

    print(f"[OPEN] https://kick.com/{username}")

    webbrowser.open_new_tab(url)


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

    # Menyimpan status channel sebelumnya
    previous_status = {
        channel.lower(): False
        for channel in channels
    }

    while True:

        for channel in channels:
            channel = channel.strip()

            if not channel:
                continue

            live = check_live(channel)

            if live:
                print(f"[LIVE] {channel}")

                # Hanya buka ketika berubah dari offline -> live
                if not previous_status[channel.lower()]:
                    open_stream(channel)

            else:
                print(f"[OFFLINE] {channel}")

            previous_status[channel.lower()] = live

        print("-" * 55)
        print(f"Menunggu {interval} detik...")
        print("-" * 55)

        time.sleep(interval)


if __name__ == "__main__":
    main()
