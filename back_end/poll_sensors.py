import requests
import time

database_url = "https://iot-uit-hmn-default-rtdb.asia-southeast1.firebasedatabase.app"

def poll_sensors(interval=5):
    print(f"Bắt đầu polling dữ liệu sensors mỗi {interval} giây (Ctrl+C để dừng)...")
    last_data = None
    while True:
        url = f"{database_url}/sensors.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data != last_data:
                print("Dữ liệu sensors mới:")
                print(data)
                last_data = data
        else:
            print("Lỗi:", response.status_code, response.text)
        time.sleep(interval)

if __name__ == "__main__":
    poll_sensors()
