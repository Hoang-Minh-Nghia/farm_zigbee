# IoT Water Dashboard - Firebase Hosting

Triển khai trang web tĩnh (`index.html` + `dashboard.html`) lên Firebase Hosting.

## 1. Yêu cầu ban đầu
- Đã có tài khoản Google.
- Cài đặt Node.js (>= 16). Kiểm tra bằng: `node -v` và `npm -v`.
- Cài đặt Firebase CLI toàn cục:

```powershell
npm install -g firebase-tools
```

Đăng nhập Firebase:
```powershell
firebase login
```

## 2. Tạo dự án Firebase (nếu chưa có)
Vào https://console.firebase.google.com tạo một Project (ví dụ: `iot-water-dashboard`). Lấy **Project ID** (ví dụ `iot-water-dashboard`).

Sửa file `.firebaserc`:
```json
{
  "projects": { "default": "iot-water-dashboard" }
}
```

## 3. Cấu trúc triển khai
Các file chính:
- `index.html` (entry chính được rewrite cho mọi route).
- `dashboard.html` (nội dung thực tế, được tải động từ `index.html`).
- `firebase.json` (cấu hình Hosting).
- `.firebaserc` (Project ID).

`firebase.json` hiện tại:
```json
{
  "hosting": {
    "public": ".",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [
      { "source": "**", "destination": "/index.html" }
    ]
  }
}
```

## 4. Triển khai lần đầu
Trong thư mục dự án (`e:\thacsi\ki_1\iot\code`):

```powershell
firebase deploy --only hosting
```

Sau khi deploy xong, CLI sẽ in ra URL dạng:
```
Hosting URL: https://iot-water-dashboard.web.app
```
Bạn có thể truy cập ngay.

## 5. Cập nhật và redeploy
Mỗi khi sửa `dashboard.html` hoặc `index.html` chỉ cần chạy lại:
```powershell
firebase deploy --only hosting
```

## 6. Thêm custom domain (tùy chọn)
Trong Firebase Console > Hosting > Add custom domain.
1. Nhập tên miền của bạn.
2. Thêm các bản ghi DNS TXT / A theo hướng dẫn.
3. Chờ xác thực và SSL sẽ tự động cấp.

## 7. Thiết lập Cache / Headers (nâng cao)
Thêm vào `firebase.json` phần `headers` để kiểm soát cache:
```json
"headers": [
  {
    "source": "**/*.html",
    "headers": [ { "key": "Cache-Control", "value": "no-cache" } ]
  },
  {
    "source": "**/*.css",
    "headers": [ { "key": "Cache-Control", "value": "public,max-age=86400" } ]
  },
  {
    "source": "**/*.js",
    "headers": [ { "key": "Cache-Control", "value": "public,max-age=86400" } ]
  }
]
```

## 8. Bảo mật / Tích hợp dữ liệu thật
Hiện tại dữ liệu là giả lập trong JS. Để lấy dữ liệu thật:
- Sử dụng Realtime Database hoặc Firestore: thêm SDK `<script type="module">` và truy vấn.
- Hoặc gọi API từ server riêng (Express, Cloud Functions).
- Không để lộ API keys bí mật (Firebase config public là được phép share).

### Tích hợp Firebase Realtime Database
1. Tạo Web App trong Console để lấy `firebaseConfig`.
2. Sao chép `firebase-config.example.js` thành `firebase-config.js` và điền giá trị thực:
   ```js
   export const firebaseConfig = {
     apiKey: "...",
     authDomain: "<PROJECT>.firebaseapp.com",
     databaseURL: "https://<PROJECT>-default-rtdb.asia-southeast1.firebasedatabase.app",
     projectId: "<PROJECT>",
     storageBucket: "<PROJECT>.appspot.com",
     messagingSenderId: "...",
     appId: "..."
   };
   ```
3. Rules thử (dev):
   ```json
   {"rules": {".read": true, ".write": true}}
   ```
4. Push dữ liệu mẫu (PowerShell):
   ```powershell
   $ts = [int][double]::Parse((Get-Date -UFormat %s)) * 1000
   $body = '{"do":7.2,"temp":26.6,"ph":7.41,"tds":530,"secchi":40,"orp":320}'
   Invoke-RestMethod -Method Put -Uri "https://<DATABASE_URL>/sensors/$ts.json" -Body $body
   ```
5. Trang sẽ tự đọc realtime nếu tìm thấy file `firebase-config.js` và init thành công.
6. Sau test: siết Rules, ví dụ validate trường:
   ```json
   {
     "rules": {
       "sensors": {
         "$ts": {
           ".read": true,
           ".write": true,
           ".validate": "newData.hasChildren(['do','temp','ph','tds','secchi','orp'])"
         }
       }
     }
   }
   ```
7. Nếu cần bảo vệ ghi: đặt `".write": "auth != null"` và thêm Firebase Authentication.


## 9. Debug thường gặp
| Vấn đề | Nguyên nhân | Cách xử lý |
|--------|-------------|------------|
| 404 Not Found | Sai Project ID | Sửa `.firebaserc` và deploy lại |
| Không load `dashboard.html` | Đổi tên file hoặc sai đường dẫn fetch | Kiểm tra `fetch('dashboard.html')` còn tồn tại file |
| CLI báo chưa login | Chưa `firebase login` | Chạy lại lệnh đăng nhập |
| Deploy chậm | Mạng yếu hoặc quá nhiều file | Giảm số file, kiểm tra kết nối |

## 10. Xóa hoặc rollback
Danh sách các phiên bản deploy:
```powershell
firebase hosting:channel:list
```
Tạo channel tạm thời (preview):
```powershell
firebase hosting:channel:deploy test-channel
```

## 11. Gợi ý cải tiến
- Thêm Service Worker cho offline (Workbox).
- Tách CSS/JS ra file riêng để cache tốt hơn.
- Dùng Firestore + bảo vệ bằng Security Rules.
- Thêm auth (Firebase Authentication) nếu cần phân quyền.

---
Nếu cần tích hợp dữ liệu thật hoặc tối ưu hiệu năng, cứ yêu cầu tiếp nhé.



// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBTmeB0WNy_89O7OnXUK_ljYlFWiLsN2jc",
  authDomain: "iot-uit-hmn.firebaseapp.com",
  databaseURL: "https://iot-uit-hmn-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "iot-uit-hmn",
  storageBucket: "iot-uit-hmn.firebasestorage.app",
  messagingSenderId: "8698529201",
  appId: "1:8698529201:web:be53c25b9e72e766b96990",
  measurementId: "G-G8B4VNQ959"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);