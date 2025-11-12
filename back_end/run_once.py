"""run_once.py
Gửi 1 bản ghi dữ liệu cảm biến mẫu lên Firebase Realtime Database.
Sao chép config.example.json thành config.json và chỉnh database_url nếu cần.
"""
from __future__ import annotations
import json, time, random, pathlib, sys
import requests

CONFIG_PATH = pathlib.Path(__file__).parent / 'config.json'

RANGES = {
    'do': (4.0, 10.0),        # mg/L
    'temp': (22.0, 32.0),     # °C
    'ph': (6.5, 8.5),         # pH
    'tds': (200, 800),        # ppm
    'secchi': (20, 60),       # cm
    'orp': (200, 450)         # mV
}

def load_config():
    if not CONFIG_PATH.exists():
        print('Không tìm thấy config.json. Sao chép config.example.json thành config.json trước.')
        sys.exit(1)
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def rand_value(low, high, decimals=2):
    val = random.uniform(low, high)
    return round(val, decimals) if decimals else int(val)

def generate_sample():
    return {
        'do': rand_value(*RANGES['do']),
        'temp': rand_value(*RANGES['temp'], 1),
        'ph': rand_value(*RANGES['ph']),
        'tds': rand_value(*RANGES['tds'], 0),
        'secchi': rand_value(*RANGES['secchi'], 0),
        'orp': rand_value(*RANGES['orp'], 0),
    }

def push_once(cfg):
    ts = int(time.time() * 1000)  # milliseconds key
    data = generate_sample()
    url = f"{cfg['database_url'].rstrip('/')}/{cfg['path']}/{ts}.json"
    try:
        resp = requests.put(url, json=data, timeout=10)
        if resp.status_code < 300:
            print('Đã gửi:', ts, data)
        else:
            print('Lỗi gửi:', resp.status_code, resp.text)
    except requests.RequestException as e:
        print('RequestException:', e)

if __name__ == '__main__':
    cfg = load_config()
    push_once(cfg)
