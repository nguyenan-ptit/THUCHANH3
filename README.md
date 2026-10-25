# CoAP Lab – THUCHANH3

## Thông tin sinh viên

| Thông tin | Chi tiết |
|-----------|---------|
| Họ tên    | [Tên sinh viên] |
| MSSV      | [Mã sinh viên] |
| Lớp       | [Lớp] |
| Môn học   | Lập trình Python với giao thức CoAP |

---

## Môi trường

| Thành phần | Phiên bản |
|-----------|----------|
| Python    | 3.10+    |
| aiocoap   | ≥ 0.4.7  |

### Cài đặt

```bash
pip install aiocoap
```

---

## Cấu trúc thư mục

```
IOT-B3/
└── bai3/
    ├── light_server_bai3.py      # CoAP Server (ObservableResource)
    ├── light_controller_bai3.py  # Controller Client (GET / PUT)
    └── light_monitor_bai3.py     # Monitoring Client (CoAP Observe)
```

---
# Bài 1 – Lập trình Python với giao thức CoAP

## Chạy chương trình

**Terminal 1 – khởi động Server:**

```bash
python coap_server_bai1.py
```

**Terminal 2 – chạy Client:**

```bash
python coap_client_bai1.py
```


## Kết quả mong đợi

**Client:**

```text

--- GET request ---
Code: 2.05 Content
Payload: Xin chao tu CoAP Server

--- Multiple POST requests ---

Sending: Xin chao tu CoAP Client - B23DCCN001 - Nguyen Van A
Code: 2.04 Changed
Payload: Server da nhan thong diep

Sending: Thong diep thu 2 - B23DCCN001 - Nguyen Van A
Code: 2.04 Changed
Payload: Server da nhan thong diep

Sending: Thong diep thu 3 - B23DCCN001 - Nguyen Van A
Code: 2.04 Changed
Payload: Server da nhan thong diep

--- GET latest message ---
Code: 2.05 Content
Payload: Thong diep thu 3 - B23DCCN001 - Nguyen Van A

--- Test URI not found ---
Code: 4.04 Not Found
Payload:
```

**Server:**

```text
CoAP Server started on port 5683
URI: coap://127.0.0.1:5683/iot/lab/message

GET request received:
URI: coap://127.0.0.1/iot/lab/message

POST request received:
Payload: Xin chao tu CoAP Client - B23DCCN001 - Nguyen Van A
Time: 14:49:42

POST request received:
Payload: Thong diep thu 2 - B23DCCN001 - Nguyen Van A
Time: 14:49:42

POST request received:
Payload: Thong diep thu 3 - B23DCCN001 - Nguyen Van A
Time: 14:49:42

GET request received:
URI: coap://127.0.0.1/iot/lab/message
```


## Bài 3 – Mô phỏng hệ thống giám sát và điều khiển đèn thông minh

### Địa chỉ & URI

| Thành phần | Giá trị |
|-----------|---------|
| Protocol  | CoAP / UDP |
| Host      | `127.0.0.1` |
| Port      | `5683` |
| URI light01 | `coap://localhost:5683/iot/lab/light01/status` |
| URI fan01   | `coap://localhost:5683/iot/lab/fan01/status`   |
| URI pump01  | `coap://localhost:5683/iot/lab/pump01/status`  |

### Cách chạy (mở 3 terminal)

**Terminal 1 – Server**

```bash
cd bai3
python light_server_bai3.py
```

**Terminal 2 – Controller Client**

```bash
cd bai3
python light_controller_bai3.py
```

Nhập lệnh:

| Lệnh     | Chức năng |
|----------|----------|
| `ON`     | Bật đèn (PUT) |
| `OFF`    | Tắt đèn (PUT) |
| `STATUS` | Xem trạng thái (GET) |
| `CHANGE` | Đổi thiết bị đang điều khiển |
| `EXIT`   | Thoát chương trình |

**Terminal 3 – Monitoring Client**

```bash
cd bai3
python light_monitor_bai3.py
```

Chọn theo dõi **một thiết bị** hoặc **tất cả** (multi-observe).

---

## Tính năng đã triển khai

### Yêu cầu cơ bản ✅

- [x] Server định nghĩa tài nguyên `/iot/lab/light01/status`
- [x] Hỗ trợ **GET** – trả về trạng thái JSON kèm timestamp
- [x] Hỗ trợ **PUT** – nhận lệnh ON/OFF và cập nhật trạng thái
- [x] Hỗ trợ **CoAP Observe** – tự động thông báo khi trạng thái đổi
- [x] Monitoring Client dùng đúng cơ chế Observe, **không** dùng vòng lặp GET

### Phần mở rộng ✅

| Tính năng mở rộng | Mô tả |
|------------------|-------|
| Kiểm tra lệnh không hợp lệ | Server trả về `4.00 Bad Request` với thông báo lỗi |
| Nhiều Monitoring Client | Tất cả cùng nhận thông báo khi trạng thái thay đổi |
| Nhiều thiết bị | `light01`, `fan01`, `pump01` – mỗi thiết bị một URI riêng |
| Timestamp trong payload | Trường `timestamp` trong JSON phản hồi |
| Ghi nhật ký ra file | File `device_state_log.txt` ghi mọi thay đổi trạng thái |
| Lệnh CHANGE | Controller Client có thể đổi thiết bị không cần khởi động lại |
| Multi-observe | Monitoring Client có thể theo dõi tất cả thiết bị đồng thời |

---

## Payload mẫu

**GET / Observe response:**

```json
{
  "device_id": "light01",
  "status": "ON",
  "timestamp": "2026-10-22 13:40:00"
}
```

**PUT request:**

```json
{
  "device_id": "light01",
  "command": "ON"
}
```

---

## Kết quả mẫu

### Terminal 1 – Server

```
CoAP Smart Light Server started on port 5683
Resource: coap://localhost:5683/iot/lab/light01/status

New Observe registration received

PUT request received:
  Device : light01
  Command: ON

  Light state changed: OFF -> ON
  Notify observers   : ON
```

### Terminal 2 – Controller

```
Nhap lenh (light01): ON

Sending PUT request...
Response Code: 2.04 Changed
Da bat light01  (trang thai hien tai: ON)

Nhap lenh (light01): STATUS

Sending GET request...
Response:
  Code   : 2.05 Content
  Device : light01
  Status : ON
  Time   : 2026-10-22 13:40:05
```

### Terminal 3 – Monitoring

```
Registering CoAP Observe...
Observe registration successful

[13:40:00] Initial State
  Device   : light01
  Status   : OFF
  >>> DEN DANG TAT <<<

[13:40:15] State Updated
  Device   : light01
  Status   : ON
  >>> DEN DANG BAT <<<
```
