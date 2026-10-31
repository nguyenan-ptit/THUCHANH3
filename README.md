# CoAP Lab – Thực hành buổi 3

Mã nguồn Python cho ba bài thực hành giao thức **CoAP trên UDP**: trao đổi thông điệp, giám sát cảm biến và điều khiển thiết bị bằng CoAP Observe.

## 1. Thông tin nhóm thực hiện

| Mã sinh viên | Họ và tên |
| --- | --- |
| B23DCCN004 | Nguyễn Văn An |
| B23DCCN914 | Đặng Kỳ Vĩ |
| B23DCCN617 | Vũ Thành Nguyên |

Repository GitHub: [nguyenan-ptit/THUCHANH3](https://github.com/nguyenan-ptit/THUCHANH3).


## 2. Cấu trúc thư mục

Thư mục repository `THUCHANH3` tương ứng với thư mục `CoAP_Lab` trong cấu trúc đề xuất của đề bài.

```text
THUCHANH3/
|-- bai1/
|   |-- coap_server_bai1.py
|   |-- coap_client_bai1.py
|-- bai2/
|   |-- sensor_server_bai2.py
|   |-- monitor_client_bai2.py
|-- bai3/
|   |-- light_server_bai3.py
|   |-- light_controller_bai3.py
|   |-- light_monitor_bai3.py
|-- evidence/
|   |-- bai1.log
|   |-- bai2.log
|   |-- bai3.log
|-- requirements.txt
|-- .gitignore
|-- README.md
```

## 3. Môi trường và cài đặt

### Phiên bản và thư viện

| Thành phần | Phiên bản / vai trò |
| --- | --- |
| Hệ điều hành hướng dẫn | Windows, sử dụng PowerShell |
| Python | 3.10 trở lên; môi trường `.venv` hiện có dùng **3.14.0** |
| `aiocoap` | **0.4.17** trong môi trường hiện có; xử lý CoAP và Observe |
| Thư viện chuẩn | `asyncio`, `json`, `datetime`, `logging`, `random`, `argparse`, `csv`, `math`, `pathlib`, `sys` |

Chỉ cần cài thêm `aiocoap`. File `requirements.txt` hiện khai báo `aiocoap` và chưa cố định phiên bản.

### Cài đặt môi trường

Cài Python, sau đó mở PowerShell ngay tại thư mục dự án `THUCHANH3` đã clone (nơi chứa file `requirements.txt`) và chạy:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Chỉ cần tạo `.venv` một lần. Nếu môi trường đã được tạo và cài đủ thư viện, chỉ cần kích hoạt để chạy chương trình. Nếu máy chỉ nhận lệnh `py`, dùng `py -3 -m venv .venv` để tạo môi trường.

Lệnh `python -m pip install -r requirements.txt` đã cài thư viện `aiocoap` được khai báo trong file, nên không cần chạy thêm lệnh cài riêng `aiocoap`.

Kiểm tra phiên bản sau khi kích hoạt môi trường (các lệnh này chỉ xem thông tin, không cài thêm thư viện):

```powershell
python --version
python -m pip show aiocoap
```

Trong **mỗi terminal mới**, mở thư mục gốc repository và kích hoạt `.venv` trước khi chạy chương trình:

```powershell
.\.venv\Scripts\Activate.ps1
```

Nếu PowerShell chặn script kích hoạt, có thể gọi trực tiếp Python trong môi trường ảo. Ví dụ:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .\bai1\coap_server_bai1.py
```

Các lệnh bên dưới đều chạy từ **thư mục gốc repository**, sau khi kích hoạt môi trường. Dùng `Ctrl+C` để dừng server hoặc monitor. Ba server cùng dùng cổng UDP `5683`, vì vậy **dừng server bài trước rồi mới chạy server bài tiếp theo**.

## 4. Địa chỉ IP, cổng và tài nguyên CoAP

Các chương trình hiện được cấu hình chạy trên cùng một máy: IP **`127.0.0.1`**, cổng **`5683`**, giao thức **CoAP/UDP**.

| Bài | URI đầy đủ | Phương thức / cơ chế |
| --- | --- | --- |
| 1 | `coap://127.0.0.1:5683/iot/lab/message` | GET, POST |
| 2 | `coap://127.0.0.1:5683/iot/lab/sensor01/data` | GET định kỳ |
| 2 | `coap://127.0.0.1:5683/iot/lab/sensor02/data` | GET định kỳ |
| 2 | `coap://127.0.0.1:5683/iot/lab/sensor03/data` | GET định kỳ |
| 3 | `coap://127.0.0.1:5683/iot/lab/light01/status` | GET, PUT, Observe |
| 3 | `coap://127.0.0.1:5683/iot/lab/fan01/status` | GET, PUT, Observe |
| 3 | `coap://127.0.0.1:5683/iot/lab/pump01/status` | GET, PUT, Observe |
| 3 | `coap://127.0.0.1:5683/.well-known/core` | GET để khám phá tài nguyên |

Muốn chạy trên nhiều máy, cần sửa địa chỉ bind của server và địa chỉ server trong các client thành IP LAN phù hợp, đồng thời cho phép lưu lượng UDP `5683` qua tường lửa.

## 5. Bài 1 – Trao đổi thông điệp bằng CoAP

### Cách chạy

**Terminal 1 – Server:**

```powershell
python .\bai1\coap_server_bai1.py
```

**Terminal 2 – Client:**

```powershell
python .\bai1\coap_client_bai1.py
```

Client tự chạy lần lượt: GET lời chào ban đầu → gửi ba POST → GET thông điệp mới nhất → GET URI không tồn tại `/iot/lab/unknown`, rồi kết thúc.

### Kết quả đạt được và minh chứng

- GET tài nguyên thông điệp trả mã `2.05 Content` và lời chào ban đầu.
- Ba POST đều trả mã `2.04 Changed`; server lưu thông điệp mới nhất và in nội dung, thời gian nhận.
- GET sau các POST trả đúng thông điệp thứ ba.
- GET URI không tồn tại trả mã `4.04 Not Found`.

Log đầy đủ: [evidence/bai1.log](evidence/bai1.log). Trích đoạn từ lần chạy với thông tin mẫu:

```text
--- GET request ---
Code: 2.05 Content
Payload: Xin chao tu CoAP Server

--- GET latest message ---
Code: 2.05 Content
Payload: Thong diep thu 3 - B23DCCN001 - Nguyen Van A

--- Test URI not found ---
Code: 4.04 Not Found
```

## 6. Bài 2 – Giám sát nhiệt độ và độ ẩm

### Cách chạy

**Terminal 1 – Sensor Server:**

```powershell
python .\bai2\sensor_server_bai2.py
```

**Terminal 2 – Monitoring Client**, mặc định theo dõi `sensor01`:

```powershell
python .\bai2\monitor_client_bai2.py
```

Để theo dõi `sensor02` và lưu dữ liệu vào CSV, dùng lệnh sau thay cho lệnh client mặc định:

```powershell
python .\bai2\monitor_client_bai2.py --device sensor02 --csv .\bai2\sensor_data.csv
```

`--device` nhận `sensor01`, `sensor02` hoặc `sensor03`. `--csv` là tùy chọn; dữ liệu được ghi thêm vào file, đường dẫn tương đối tính từ thư mục chạy lệnh và thư mục cha phải tồn tại. Có thể mở thêm client để theo dõi cảm biến khác.

### Kết quả đạt được và minh chứng

- Server mô phỏng ba cảm biến, cập nhật độc lập mỗi **3 giây**; nhiệt độ trong khoảng **20–40 °C**, độ ẩm **30–80%**.
- GET trả mẫu gần nhất dưới dạng JSON gồm `device_id`, `temperature`, `humidity`, `timestamp`; mã `2.05 Content`, Content-Format `50` (`application/json`), Max-Age `0`.
- Client gửi GET định kỳ khoảng **3 giây**, hiển thị số đo và thời gian phản hồi; timeout mỗi yêu cầu là **5 giây**.
- Cảnh báo khi nhiệt độ **> 35 °C** hoặc độ ẩm **< 40%**; hỗ trợ lưu CSV và thống kê khi kết thúc.
- Log kiểm chứng ghi nhận **6 GET, 6 mẫu hợp lệ**, timestamp thay đổi và thời gian phản hồi trung bình **4.38 ms** trong lần chạy đó. Bộ kiểm chứng hủy tác vụ sau khoảng 16,2 giây để thu thống kê.

Log đầy đủ: [evidence/bai2.log](evidence/bai2.log). Trích đoạn:

```text
[2026-10-30T04:01:06.586] Received sensor data
Device: sensor02
Temperature: 39.8 C
Humidity: 36.3 %
Sensor timestamp: 2026-10-30T04:01:06.222
Response time: 6.19 ms
CANH BAO: Nhiet do cao
CANH BAO: Do am thap
```

Số đo được sinh ngẫu nhiên nên mỗi lần chạy có thể cho kết quả khác nhau.

## 7. Bài 3 – Giám sát và điều khiển thiết bị bằng CoAP Observe

### Cách chạy

Mở ba terminal theo thứ tự **Server → Monitor → Controller**.

**Terminal 1 – Smart Light Server:**

```powershell
python .\bai3\light_server_bai3.py
```

**Terminal 2 – Monitoring Client:**

```powershell
python .\bai3\light_monitor_bai3.py
```

Ở menu đầu, nhập `1` hoặc Enter để theo dõi một thiết bị, sau đó chọn `1`/`2`/`3` hoặc tên `light01`/`fan01`/`pump01`. Nhập `2` ở menu đầu để theo dõi cả ba thiết bị đồng thời.

**Terminal 3 – Controller Client:**

```powershell
python .\bai3\light_controller_bai3.py
```

Chọn thiết bị bằng số thứ tự hoặc tên; Enter chọn `light01`. Các lệnh điều khiển:

| Lệnh | Chức năng |
| --- | --- |
| `ON` | Gửi PUT để bật thiết bị |
| `OFF` | Gửi PUT để tắt thiết bị |
| `STATUS` | Gửi GET để xem trạng thái hiện tại |
| `CHANGE` | Chọn thiết bị khác |
| `EXIT` | Thoát Controller Client |

Để kiểm tra, chọn `light01` ở monitor và controller, rồi lần lượt nhập `STATUS`, `ON`, `STATUS`, `ON`, `OFF`. Monitor nhận trạng thái ban đầu và các thay đổi `OFF → ON → OFF`; lệnh `ON` lặp lại khi thiết bị đã bật không tạo thêm thông báo thay đổi.

Server ghi các lần đổi trạng thái vào `device_state_log.txt` tại **thư mục chạy lệnh**. Với cách chạy ở trên, file nằm ở gốc repository; nếu chạy server từ thư mục `bai3`, file nằm trong `bai3`.

### Định dạng dữ liệu

Payload PUT bật thiết bị:

```json
{
  "device_id": "light01",
  "command": "ON"
}
```

Payload JSON phản hồi GET, PUT hoặc thông báo Observe có dạng:

```json
{
  "device_id": "light01",
  "status": "ON",
  "timestamp": "2026-10-30 04:03:23"
}
```

### Kết quả đạt được và minh chứng

- GET trả trạng thái hiện tại với mã `2.05 Content`; PUT `ON`/`OFF` trả mã `2.04 Changed`.
- Monitor đăng ký **CoAP Observe** để nhận thông báo khi trạng thái đổi. Bài 3 dùng Observe; Bài 2 dùng GET định kỳ.
- Hỗ trợ ba thiết bị, nhiều monitor và chế độ theo dõi tất cả thiết bị.
- Log đã kiểm chứng **hai monitor đồng thời** cùng nhận thay đổi `OFF → ON → OFF`, không có thông báo mới khi lặp lại `ON`, và có đúng hai dòng nhật ký thay đổi trạng thái.
- Lệnh PUT không hợp lệ như `INVALID` hoặc payload sai cú pháp JSON trả mã `4.00 Bad Request`.
- GET `/.well-known/core` liệt kê các tài nguyên có hỗ trợ Observe.

Log đầy đủ: [evidence/bai3.log](evidence/bai3.log). Trích đoạn monitor:

```text
Observe registration successful

[04:03:23] Initial State
  Device   : light01
  Status   : OFF

[04:03:23] State Updated
  Device   : light01
  Status   : ON

[04:03:24] State Updated
  Device   : light01
  Status   : OFF
```

Log Bài 3 lưu cả lỗi khởi động trước đây khi bind `0.0.0.0` trên Windows và lần chạy thành công khi đổi sang `127.0.0.1` trong bộ kiểm chứng. Mã nguồn hiện tại đã dùng `bind=("127.0.0.1", 5683)` để phù hợp với các client và transport trên Windows.

## 8. Hình thức nộp bài qua GitHub

Nộp đường dẫn repository: **[https://github.com/nguyenan-ptit/THUCHANH3](https://github.com/nguyenan-ptit/THUCHANH3)**.

Trước khi nộp, bảo đảm cả bảy file Python của ba bài, `requirements.txt`, `README.md` và các log trong `evidence/` đã được commit và push lên GitHub. Đối chiếu thông tin sinh viên trong mã nguồn, README và minh chứng. Không đưa môi trường ảo `.venv` hoặc các file cache Python vào repository.
