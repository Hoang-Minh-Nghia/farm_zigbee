# Backend Data Pusher (Firebase Realtime Database)

Scripts Python gửi dữ liệu cảm biến giả lập lên Firebase Realtime Database để hiển thị trên dashboard.

## 1. Chuẩn bị
- Cài Python 3.10+.
- Tạo virtualenv (khuyến nghị).
- Sao chép `config.example.json` thành `config.json` và chỉnh `database_url` nếu khác.

## 2. Cài thư viện
```powershell
cd E:\thacsi\ki_1\iot\code\back_end
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Cấu hình `config.json`
```json
{
  "database_url": "https://iot-uit-hmn-default-rtdb.asia-southeast1.firebasedatabase.app",
  "path": "sensors",
  "push_interval_seconds": 5,
  "max_queue": 200
}
```
Giải thích:
- `database_url`: URL Realtime Database.
- `path`: node gốc để lưu dữ liệu.
- `push_interval_seconds`: khoảng thời gian giữa các lần gửi.
- `max_queue`: số lượng tối đa bản ghi lưu tạm khi lỗi mạng.

## 4. Gửi một bản ghi thử
```powershell
python run_once.py
```
Xem trên console hoặc Firebase Console > Realtime Database.

## 5. Gửi liên tục
```powershell
python push_data.py
```
Dừng lại bằng:
```powershell
New-Item -ItemType File STOP
```
Hoặc Ctrl+C.

## 6. Chạy nền (Windows Task Scheduler)
Tạo task chạy `python push_data.py` với trigger Startup hoặc theo lịch.

## 7. Phạm vi giá trị cảm biến
| Sensor | Range | Đơn vị |
|--------|-------|--------|
| DO     | 4.0 - 10.0 | mg/L |
| Temp   | 22.0 - 32.0 | °C |
| pH     | 6.5 - 8.5 | pH |
| TDS    | 200 - 800 | ppm |
| Secchi | 20 - 60 | cm |
| ORP    | 200 - 450 | mV |

## 8. Kiểm thử nhanh
Sau khi chạy `run_once.py`, refresh dashboard: nếu config Firebase đã hoạt động thì điểm mới xuất hiện.
Nếu thấy mock: kiểm tra `firebase-config.js` hoặc rules.

## 9. Mở rộng thật
- Kết nối thiết bị thật (ESP32) gửi HTTP PUT tương tự.
- Thêm xác thực bằng token nếu siết Rules.
- Log dữ liệu thô vào file hoặc Firestore.

## 10. Xử lý sự cố
| Vấn đề | Nguyên nhân | Giải pháp |
|--------|-------------|-----------|
| 401 / Permission denied | Rules chặt, chưa bật đọc/ghi | Nới rules tạm thời cho dev |
| Kết nối timeout | Mạng yếu hoặc URL sai | Kiểm tra database_url |
| Giá trị ngoài phạm vi | Ranges chưa khớp thực tế | Điều chỉnh bảng RANGES |

---
Cần thêm script xuất CSV hoặc cảnh báo ngưỡng? Nói mình để bổ sung.
