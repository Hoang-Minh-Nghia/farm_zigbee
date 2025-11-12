// Đọc dữ liệu từ Firebase Realtime Database
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.1/firebase-app.js";
import { getDatabase, ref, onValue } from "https://www.gstatic.com/firebasejs/10.13.1/firebase-database.js";

const firebaseConfig = {
  apiKey: "AIzaSyBTmeB0WNy_89O7OnXUK_ljYlFWiLsN2jc",
  authDomain: "iot-uit-hmn.firebaseapp.com",
  databaseURL: "https://iot-uit-hmn-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "iot-uit-hmn",
  storageBucket: "iot-uit-hmn.appspot.com",
  messagingSenderId: "8698529201",
  appId: "1:8698529201:web:be53c25b9e72e766b96990"
};

const app = initializeApp(firebaseConfig);
const db = getDatabase(app);

// Đọc realtime node 'sensors'
const sensorsRef = ref(db, 'sensors');
onValue(sensorsRef, (snapshot) => {
  const data = snapshot.val();
  console.log('Sensors data:', data);
  // Chỉ hiển thị tối đa 10 bản ghi cuối để tránh tràn trang
  const containerId = 'realtime-output';
  let container = document.getElementById(containerId);
  if (!container) {
    container = document.createElement('div');
    container.id = containerId;
    container.style.cssText = 'position:fixed;top:8px;right:8px;max-height:60vh;overflow:auto;background:#fff;padding:8px 12px;border:1px solid #eee;font-size:12px;border-radius:6px;box-shadow:0 2px 6px rgba(0,0,0,0.15);width:280px;z-index:5000;';
    document.body.appendChild(container);
  }
  const entries = Object.entries(data || {}).sort((a,b)=>a[0].localeCompare(b[0]));
  const lastTen = entries.slice(-10);
  container.innerHTML = '<strong>Last 10 records:</strong><br><pre style="margin:4px 0;white-space:pre-wrap;word-break:break-word;">' +
    JSON.stringify(Object.fromEntries(lastTen), null, 2) + '</pre>';
});
