import requests
import time

database_url = "https://iot-uit-hmn-default-rtdb.asia-southeast1.firebasedatabase.app"

def get_sensors_data():
    url = f"{database_url}/sensors.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("Sensors data:")
        print(data)
    else:
        print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    print("Bắt đầu polling dữ liệu (Ctrl+C để dừng)...")
    while True:
        get_sensors_data()
        time.sleep(5)  # Lấy lại dữ liệu mỗi 5 giây
