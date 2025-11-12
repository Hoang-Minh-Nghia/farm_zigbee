"""push_data.py
Script gửi dữ liệu giả lập lên Firebase Realtime Database.

ĐÃ CẬP NHẬT KEY MỚI (phục vụ dashboard mới):
    airTemp       (°C)          – Nhiệt độ không khí
    airHumidity   (%)           – Độ ẩm không khí
    soilHumidity  (%)           – Độ ẩm đất
    light         (lux)         – Cường độ ánh sáng
    pin           (%)           – Mức pin
    connStatus    (0|1)         – Trạng thái kết nối (1=Online,0=Offline)

Trước đây: do, temp, ph, tds, secchi, orp (đã bỏ). Nếu cần tương thích song song, thêm cả hai bộ key.

Sao chép config.example.json -> config.json và chỉnh database_url + path (ví dụ "sensors").
Có queue tạm nếu lỗi mạng và cơ chế backoff.

Chạy thử một lần:  python push_data.py --once
Chạy liên tục:     python push_data.py
Tạo file STOP trong thư mục này để dừng vòng lặp.
"""
from __future__ import annotations
import json, time, random, pathlib, sys, threading
import requests
from typing import Dict, Any, List

CONFIG_PATH = pathlib.Path(__file__).parent / 'config.json'
STOP_FILE = pathlib.Path(__file__).parent / 'STOP'

RANGES = {
    'airTemp': (20.0, 38.0),          # °C
    'airHumidity': (40.0, 95.0),      # %
    'soilHumidity': (20.0, 90.0),     # %
    'light': (200, 12000),            # lux
    'pin': (30, 100),                 # %
    # connStatus: 0 hoặc 1 (80% online) không cần range
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

def generate_sample(include_old: bool = False):
    """Tạo một bản ghi giả lập.
    include_old: nếu True, thêm cả các key cũ để chuyển tiếp.
    """
    data = {
        'airTemp': rand_value(*RANGES['airTemp'], 1),
        'airHumidity': rand_value(*RANGES['airHumidity'], 1),
        'soilHumidity': rand_value(*RANGES['soilHumidity'], 1),
        'light': rand_value(*RANGES['light'], 0),
        'pin': rand_value(*RANGES['pin'], 0),
        'connStatus': 1 if random.random() < 0.8 else 0,
    }
    if include_old:
        # ánh xạ tạm: giữ logic cũ để giai đoạn chuyển tiếp nếu vẫn còn dashboard cũ
        data.update({
            'do': round(random.uniform(4.0,10.0),2),
            'temp': data['airTemp'],
            'ph': round(random.uniform(6.5,8.5),2),
            'tds': int(random.uniform(200,800)),
            'secchi': int(random.uniform(20,60)),
            'orp': int(random.uniform(200,450)),
        })
    return data

class QueueSender:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        self.queue: List[Dict[str, Any]] = []
        self.max_queue = cfg.get('max_queue', 200)
        self.lock = threading.Lock()

    def enqueue(self, item: Dict[str, Any]):
        with self.lock:
            self.queue.append(item)
            if len(self.queue) > self.max_queue:
                # bỏ bản ghi cũ nhất
                self.queue.pop(0)

    def flush(self):
        with self.lock:
            if not self.queue:
                return
            remaining = []
            for item in self.queue:
                if not push_record(self.cfg, item['ts'], item['data']):
                    remaining.append(item)
            self.queue = remaining

BACKOFF_BASE = 2
MAX_BACKOFF = 60  # giây

def push_record(cfg: Dict[str, Any], ts: int, data: Dict[str, Any]) -> bool:
    url = f"{cfg['database_url'].rstrip('/')}/{cfg['path']}/{ts}.json"
    try:
        resp = requests.put(url, json=data, timeout=10)
        if resp.status_code < 300:
            print(f"Đã gửi {ts}: {data}")
            return True
        else:
            print(f"Lỗi {resp.status_code} gửi {ts}: {resp.text}")
            return False
    except requests.RequestException as e:
        print('RequestException:', e)
        return False


def main():
    cfg = load_config()
    interval = cfg.get('push_interval_seconds', 5)
    include_old = bool(cfg.get('include_old_keys', False))
    sender = QueueSender(cfg)
    backoff = 1

    print('Bắt đầu gửi dữ liệu mỗi', interval, 'giây. Tạo file STOP để kết thúc.')
    single_run = '--once' in sys.argv

    def cycle():
        nonlocal backoff
        ts = int(time.time() * 1000)  # dùng millisecond timestamp làm key
        data = generate_sample(include_old=include_old)
        success = push_record(cfg, ts, data)
        if not success:
            sender.enqueue({'ts': ts, 'data': data})
            print('Đưa vào queue, kích thước:', len(sender.queue))
            time.sleep(backoff)
            backoff = min(backoff * BACKOFF_BASE, MAX_BACKOFF)
        else:
            backoff = 1
            sender.flush()
            if not single_run:
                time.sleep(interval)

    if single_run:
        cycle()
        return

    while True:
        if STOP_FILE.exists():
            print('Phát hiện STOP; thoát...')
            break
        cycle()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Ngừng bởi người dùng.')
