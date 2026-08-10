# kick-auto-stream
Auto-monitor multiple KICK channels and automatically open live streams in your browser.
# KICK Auto Stream

Python script untuk memantau beberapa channel KICK.

Jika channel berubah dari OFFLINE menjadi LIVE,
script otomatis membuka channel tersebut di browser.

## Features

- Multi-channel monitoring
- Otomatis mendeteksi LIVE
- Otomatis membuka browser
- Satu tab untuk setiap channel
- Bisa menentukan interval pengecekan
- Tidak membutuhkan login

## Installation

Install Python 3.

Kemudian:

pip install -r requirements.txt

## Configuration

Edit `config.json`.

Contoh:

{
    "channels": [
        "channel1",
        "channel2",
        "channel3"
    ],
    "check_interval": 60
}

`check_interval` menggunakan detik.

30 = 30 detik
60 = 1 menit
300 = 5 menit

## Run

Jalankan:

python main.py

## Stop

Tekan:

CTRL + C
