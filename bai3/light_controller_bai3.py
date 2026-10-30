"""
Bai 3 - Chuong trinh 2: Light Controller Client
Cho phep nguoi dung nhap lenh ON/OFF/STATUS/EXIT de dieu khien den

Ho ten: Vu Thanh Nguyen
Ma sinh vien: B23DCCN617
"""

import asyncio
import json
import sys

import aiocoap
from aiocoap import Message, Code

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5683

# Danh sach thiet bi co the dieu khien (mo rong)
AVAILABLE_DEVICES = ["light01", "fan01", "pump01"]


def build_uri(device_id: str) -> str:
    return f"coap://{SERVER_HOST}:{SERVER_PORT}/iot/lab/{device_id}/status"


# ===========================================================
# Gui yeu cau GET – lay trang thai hien tai
# ===========================================================
async def send_get(protocol, device_id: str):
    uri = build_uri(device_id)
    print(f"\nSending GET request...")
    print(f"URI: {uri}")

    try:
        request = Message(code=Code.GET)
        request.set_request_uri(uri)
        response = await asyncio.wait_for(protocol.request(request).response, timeout=5.0)
        payload_str = response.payload.decode("utf-8")
        print(f"\nResponse:")
        print(f"  Code   : {response.code}")
        try:
            data = json.loads(payload_str)
            print(f"  Device : {data.get('device_id', 'N/A')}")
            print(f"  Status : {data.get('status', 'N/A')}")
            ts = data.get("timestamp", "")
            if ts:
                print(f"  Time   : {ts}")
        except json.JSONDecodeError:
            print(f"  Payload: {payload_str}")
    except asyncio.TimeoutError:
        print("  LOI: Timeout – Server khong phan hoi trong 5 giay.")
    except Exception as exc:
        print(f"  LOI: {exc}")


# ===========================================================
# Gui yeu cau PUT – thay doi trang thai
# ===========================================================
async def send_put(protocol, device_id: str, command: str):
    uri = build_uri(device_id)
    payload = json.dumps({"device_id": device_id, "command": command}).encode("utf-8")

    print(f"\nSending PUT request...")
    print(f"URI    : {uri}")
    print(f"Command: {command}")

    try:
        request = Message(code=Code.PUT, payload=payload)
        request.set_request_uri(uri)
        request.opt.content_format = 50  # application/json
        response = await asyncio.wait_for(protocol.request(request).response, timeout=5.0)
        print(f"\nResponse Code: {response.code}")

        try:
            resp_data = json.loads(response.payload.decode("utf-8"))
            status = resp_data.get("status", "N/A")
            if command == "ON":
                print(f"Da bat {device_id}  (trang thai hien tai: {status})")
            else:
                print(f"Da tat {device_id}  (trang thai hien tai: {status})")
        except Exception:
            print(f"Payload phan hoi: {response.payload.decode('utf-8', errors='replace')}")

    except asyncio.TimeoutError:
        print("  LOI: Timeout – Server khong phan hoi trong 5 giay.")
    except Exception as exc:
        print(f"  LOI: {exc}")


# ===========================================================
# Chon thiet bi
# ===========================================================
def choose_device() -> str:
    print("\nDanh sach thiet bi:")
    for i, dev in enumerate(AVAILABLE_DEVICES, start=1):
        print(f"  {i}. {dev}")
    while True:
        choice = input("Chon so thu tu thiet bi (mac dinh 1 - light01): ").strip()
        if choice == "":
            return AVAILABLE_DEVICES[0]
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(AVAILABLE_DEVICES):
                return AVAILABLE_DEVICES[idx]
        # Thu xem nguoi dung nhap ten thiet bi truc tiep
        if choice in AVAILABLE_DEVICES:
            return choice
        print("Lua chon khong hop le, thu lai.")


# ===========================================================
# Vong lap chinh
# ===========================================================
async def main():
    print("=" * 50)
    print("  Light Controller Client")
    print(f"  Server: coap://{SERVER_HOST}:{SERVER_PORT}")
    print("=" * 50)

    try:
        protocol = await aiocoap.Context.create_client_context()
    except Exception as exc:
        print(f"Khong the khoi tao CoAP client: {exc}")
        sys.exit(1)

    device_id = choose_device()
    print(f"\nDang dieu khien thiet bi: {device_id}")
    print("Lenh: ON | OFF | STATUS | CHANGE | EXIT")

    while True:
        try:
            cmd = input(f"\nNhap lenh ({device_id}): ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print("\nDong chuong trinh.")
            break

        if cmd == "EXIT":
            print("Ket thuc chuong trinh.")
            break
        elif cmd in ("ON", "OFF"):
            await send_put(protocol, device_id, cmd)
        elif cmd == "STATUS":
            await send_get(protocol, device_id)
        elif cmd == "CHANGE":
            device_id = choose_device()
            print(f"Da chuyen sang thiet bi: {device_id}")
        elif cmd == "":
            pass  # Bo qua dong trong
        else:
            print(f"Lenh '{cmd}' khong hop le. Chi chap nhan: ON, OFF, STATUS, CHANGE, EXIT.")

    await protocol.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nController Client da dung.")
