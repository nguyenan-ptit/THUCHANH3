"""Bai 2: GET du lieu cam bien moi 3 giay, canh bao va luu CSV tuy chon."""

import argparse
import asyncio
import csv
from datetime import datetime
import json
import math
from pathlib import Path

from aiocoap import Context, Message, GET, error


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5683
POLL_INTERVAL = 3
REQUEST_TIMEOUT = 5
SENSOR_IDS = ("sensor01", "sensor02", "sensor03")
CSV_FIELDS = (
    "received_at", "device_id", "temperature", "humidity", "timestamp",
    "response_time_ms",
)


def build_uri(device_id: str) -> str:
    return f"coap://{SERVER_HOST}:{SERVER_PORT}/iot/lab/{device_id}/data"


def parse_sensor_data(response, device_id: str) -> dict:
    if not response.code.is_successful():
        raise ValueError(f"Server tra ve ma loi CoAP: {response.code}")
    if response.opt.content_format != 50:
        raise ValueError("Content-Format phai la application/json (50)")

    data = json.loads(response.payload.decode("utf-8"))
    if not isinstance(data, dict) or data.get("device_id") != device_id:
        raise ValueError("Ma thiet bi trong JSON khong khop voi yeu cau")
    for field in ("temperature", "humidity"):
        value = data.get(field)
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value)):
            raise ValueError(f"Truong {field} phai la so huu han")
    if not 0 <= data["humidity"] <= 100:
        raise ValueError("Do am phai nam trong khoang 0 den 100 %")
    if "timestamp" in data and not isinstance(data["timestamp"], str):
        raise ValueError("Truong timestamp phai la chuoi")
    return data


def display_data(data: dict, received_at: str, response_time_ms: float):
    print(f"\n[{received_at}] Received sensor data")
    print(f"Device: {data['device_id']}")
    print(f"Temperature: {data['temperature']:.1f} C")
    print(f"Humidity: {data['humidity']:.1f} %")
    if data.get("timestamp"):
        print(f"Sensor timestamp: {data['timestamp']}")
    print(f"Response time: {response_time_ms:.2f} ms")

    high_temperature = data["temperature"] > 35
    low_humidity = data["humidity"] < 40
    if high_temperature:
        print("CANH BAO: Nhiet do cao")
    if low_humidity:
        print("CANH BAO: Do am thap")
    if not high_temperature and not low_humidity:
        print("Trang thai: Binh thuong")
    print("-" * 40)


async def monitor(protocol, device_id: str, csv_file=None):
    writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS) if csv_file else None
    if writer and csv_file.tell() == 0:
        writer.writeheader()
        csv_file.flush()

    uri = build_uri(device_id)
    get_count = 0
    sample_count = 0
    total_response_ms = 0.0
    loop = asyncio.get_running_loop()
    print(f"Monitoring CoAP Client\nURI: {uri}")
    print(f"Gui GET moi {POLL_INTERVAL} giay. Nhan Ctrl+C de dung.")

    try:
        while True:
            started_at = loop.time()
            get_count += 1
            try:
                request = Message(code=GET, uri=uri, accept=50)
                response = await asyncio.wait_for(
                    protocol.request(request).response, timeout=REQUEST_TIMEOUT
                )
                response_ms = (loop.time() - started_at) * 1000
                data = parse_sensor_data(response, device_id)
                received_at = datetime.now().isoformat(timespec="milliseconds")
                sample_count += 1
                total_response_ms += response_ms
                display_data(data, received_at, response_ms)
                if writer:
                    writer.writerow({
                        "received_at": received_at,
                        "device_id": data["device_id"],
                        "temperature": data["temperature"],
                        "humidity": data["humidity"],
                        "timestamp": data.get("timestamp", ""),
                        "response_time_ms": f"{response_ms:.2f}",
                    })
                    csv_file.flush()
            except asyncio.TimeoutError:
                print(f"LOI: Server khong phan hoi trong {REQUEST_TIMEOUT} giay.")
            except error.Error as exc:
                print(f"LOI ket noi CoAP: {exc}")
            except (ValueError, UnicodeDecodeError) as exc:
                print(f"LOI du lieu cam bien: {exc}")

            # Tinh chu ky tu luc gui GET, khong cong them thoi gian phan hoi.
            # Sau loi ket noi, luon cach lan GET truoc it nhat 3 giay.
            await asyncio.sleep(max(0, POLL_INTERVAL - (loop.time() - started_at)))
    finally:
        print(f"\nTong so GET: {get_count}")
        print(f"So mau hop le: {sample_count}")
        if sample_count:
            print(f"Thoi gian phan hoi trung binh: {total_response_ms / sample_count:.2f} ms")
        else:
            print("Chua co mau hop le de tinh thoi gian phan hoi trung binh.")


async def main(device_id: str, csv_path=None):
    protocol = await Context.create_client_context()
    try:
        if csv_path is None:
            await monitor(protocol, device_id)
        else:
            # Duong dan tuong doi duoc tinh tu thu muc chay lenh.
            with csv_path.open("a", newline="", encoding="utf-8") as csv_file:
                print(f"Luu du lieu vao: {csv_path.resolve()}")
                await monitor(protocol, device_id, csv_file)
    finally:
        await protocol.shutdown()


def parse_args():
    parser = argparse.ArgumentParser(description="Giam sat cam bien CoAP bang GET dinh ky")
    parser.add_argument("--device", choices=SENSOR_IDS, default="sensor01",
                        help="Ma cam bien can theo doi (mac dinh: sensor01)")
    parser.add_argument("--csv", type=Path, help="Ghi them cac mau hop le vao file CSV")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        asyncio.run(main(args.device, args.csv))
    except KeyboardInterrupt:
        print("\nMonitoring CoAP Client da dung.")
    except (OSError, error.Error) as exc:
        print(f"Khong the chay client: {exc}")
        raise SystemExit(1)
