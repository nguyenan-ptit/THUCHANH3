"""
Bai 3 - Chuong trinh 3: Light Monitoring Client (CoAP Observe)
Su dung co che Observe de tu dong nhan thong bao khi trang thai den thay doi.
KHONG dung vong lap GET dinh ky.

Ho ten: B23DCCN617
Ma sinh vien: Vu Thanh Nguyen
"""

import asyncio
import json
import sys
import datetime

import aiocoap
from aiocoap import Message, Code

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5683

# Danh sach thiet bi co the theo doi (mo rong)
AVAILABLE_DEVICES = ["light01", "fan01", "pump01"]

_first_notification = True  # Danh dau lan dau nhan (initial state)


# ===========================================================
# Xu ly moi thong bao Observe nhan duoc
# ===========================================================
def handle_observation(response: Message, device_id: str):
    global _first_notification
    ts = datetime.datetime.now().strftime("%H:%M:%S")

    try:
        data = json.loads(response.payload.decode("utf-8"))
        status = data.get("status", "N/A")
        server_ts = data.get("timestamp", "")

        if _first_notification:
            label = "Initial State"
            _first_notification = False
        else:
            label = "State Updated"

        print(f"\n[{ts}] {label}")
        print(f"  Device   : {data.get('device_id', device_id)}")
        print(f"  Status   : {status}")
        if server_ts:
            print(f"  Server TS: {server_ts}")

        # Hien thi bien dong trang thai ro rang hon
        if status == "ON":
            print("  >>> DEN DANG BAT <<<")
        else:
            print("  >>> DEN DANG TAT <<<")

    except (json.JSONDecodeError, UnicodeDecodeError):
        print(f"\n[{ts}] Nhan thong bao (raw): {response.payload!r}")
    except Exception as exc:
        print(f"\n[{ts}] Loi xu ly thong bao: {exc}")


# ===========================================================
# Chon thiet bi can theo doi
# ===========================================================
def choose_device() -> str:
    print("\nDanh sach thiet bi co the theo doi:")
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
        if choice in AVAILABLE_DEVICES:
            return choice
        print("Lua chon khong hop le, thu lai.")


# ===========================================================
# Dang ky Observe va giu ket noi
# ===========================================================
async def observe_device(protocol, device_id: str):
    global _first_notification
    _first_notification = True

    uri = f"coap://{SERVER_HOST}:{SERVER_PORT}/iot/lab/{device_id}/status"
    print(f"\nRegistering CoAP Observe...")
    print(f"URI: {uri}")

    request = Message(code=Code.GET)
    request.set_request_uri(uri)
    request.opt.observe = 0  # Dang ky Observe

    try:
        obs = protocol.request(request)
    except Exception as exc:
        print(f"Khong the gui yeu cau Observe: {exc}")
        return

    # Nhan phan hoi dau tien (initial state)
    try:
        initial = await asyncio.wait_for(obs.response, timeout=5.0)
        if initial.code.is_successful():
            print("Observe registration successful")
            handle_observation(initial, device_id)
        else:
            print(f"Observe that bai – Server tra ve: {initial.code}")
            return
    except asyncio.TimeoutError:
        print("LOI: Timeout khi dang ky Observe (Server khong phan hoi trong 5 giay).")
        return

    # Lang nghe cac thong bao tiep theo
    print("\nDang theo doi... (Nhan Ctrl+C de dung)\n" + "-" * 45)
    try:
        async for notification in obs.observation:
            handle_observation(notification, device_id)
    except aiocoap.error.NotObservable:
        print("\nServer khong ho tro Observe cho tai nguyen nay.")
    except asyncio.CancelledError:
        pass
    except Exception as exc:
        print(f"\nLoi trong qua trinh Observe: {exc}")
    finally:
        obs.observation.cancel()


# ===========================================================
# Theo doi nhieu thiet bi dong thoi (mo rong)
# ===========================================================
async def observe_multiple(protocol, device_ids: list):
    """Theo doi nhieu thiet bi cung mot luc bang asyncio."""
    tasks = [asyncio.create_task(observe_device(protocol, did)) for did in device_ids]
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


# ===========================================================
# Diem khoi chay chinh
# ===========================================================
async def main():
    print("=" * 50)
    print("  Light Monitoring Client (CoAP Observe)")
    print(f"  Server: coap://{SERVER_HOST}:{SERVER_PORT}")
    print("=" * 50)

    try:
        protocol = await aiocoap.Context.create_client_context()
    except Exception as exc:
        print(f"Khong the khoi tao CoAP client: {exc}")
        sys.exit(1)

    # Cho phep chon theo doi mot hoac nhieu thiet bi
    print("\nBan muon theo doi bao nhieu thiet bi?")
    print("  1. Mot thiet bi")
    print("  2. Tat ca thiet bi (multi-observe)")
    mode = input("Chon (mac dinh 1): ").strip()

    if mode == "2":
        print(f"\nDang theo doi TAT CA thiet bi: {AVAILABLE_DEVICES}")
        await observe_multiple(protocol, AVAILABLE_DEVICES)
    else:
        device_id = choose_device()
        await observe_device(protocol, device_id)

    await protocol.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nMonitoring Client da dung.")
