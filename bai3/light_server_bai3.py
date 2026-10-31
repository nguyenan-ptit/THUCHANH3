"""
Bai 3 - Chuong trinh 1: Smart Light CoAP Server
Mo phong he thong giam sat va dieu khien den thong minh bang CoAP Observe

Ho ten: Vu Thanh Nguyen
Ma sinh vien: B23DCCN617
"""

import asyncio
import json
import logging
import datetime

import aiocoap
import aiocoap.resource as resource
from aiocoap import Message, Code

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ===========================================================
# Cac thiet bi duoc quan ly boi server (mo rong: nhieu thiet bi)
# ===========================================================
DEVICES = {
    "light01": {"status": "OFF", "description": "Den phong khach"},
    "fan01":   {"status": "OFF", "description": "Quat tran phong ngu"},
    "pump01":  {"status": "OFF", "description": "May bom nuoc"},
}

# Log trang thai thay doi ra file
LOG_FILE = "device_state_log.txt"


def write_state_log(device_id: str, old_status: str, new_status: str):
    """Ghi nhat ky thay doi trang thai thiet bi ra file."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {device_id}: {old_status} -> {new_status}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)


# ===========================================================
# Lop tai nguyen thiet bi – ho tro GET, PUT, va Observe
# ===========================================================
class SmartDeviceResource(resource.ObservableResource):
    """
    Tai nguyen CoAP dai dien cho mot thiet bi thong minh.
    URI: /iot/lab/<device_id>/status
    """

    def __init__(self, device_id: str):
        super().__init__()
        if device_id not in DEVICES:
            raise ValueError(f"Device '{device_id}' not configured in DEVICES dict.")
        self.device_id = device_id

    # ----------------------------------------------------------
    # Tra ve payload JSON cua trang thai hien tai
    # ----------------------------------------------------------
    def _build_payload(self) -> bytes:
        state = DEVICES[self.device_id]
        payload = {
            "device_id": self.device_id,
            "status": state["status"],
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        return json.dumps(payload).encode("utf-8")

    # ----------------------------------------------------------
    # GET – tra ve trang thai hien tai
    # ----------------------------------------------------------
    async def render_get(self, request: Message) -> Message:
        logger.info("GET request received: /iot/lab/%s/status", self.device_id)
        response = Message(
            code=Code.CONTENT,
            payload=self._build_payload(),
        )
        response.opt.content_format = 50  # application/json
        return response

    # ----------------------------------------------------------
    # PUT – cap nhat trang thai thiet bi
    # ----------------------------------------------------------
    async def render_put(self, request: Message) -> Message:
        try:
            data = json.loads(request.payload.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.warning("PUT: Payload khong hop le")
            return Message(code=Code.BAD_REQUEST, payload=b"Payload phai la JSON hop le")

        command = data.get("command", "").strip().upper()
        recv_device = data.get("device_id", "")

        print(f"\nPUT request received:")
        print(f"  Device : {recv_device}")
        print(f"  Command: {command}")

        # Kiem tra lenh hop le
        if command not in ("ON", "OFF"):
            logger.warning("Lenh khong hop le: %s", command)
            return Message(
                code=Code.BAD_REQUEST,
                payload=f"Lenh khong hop le '{command}'. Chi chap nhan ON hoac OFF.".encode(),
            )

        old_status = DEVICES[self.device_id]["status"]
        new_status = command

        # Chi cap nhat va notify khi trang thai thuc su thay doi
        if old_status != new_status:
            DEVICES[self.device_id]["status"] = new_status
            write_state_log(self.device_id, old_status, new_status)
            print(f"  Light state changed: {old_status} -> {new_status}")
            print(f"  Notify observers   : {new_status}")
            # Thong bao den tat ca observer dang dang ky
            self.updated_state()
        else:
            print(f"  Trang thai khong doi (da la {old_status})")

        response = Message(
            code=Code.CHANGED,
            payload=self._build_payload(),
        )
        response.opt.content_format = 50
        return response


# ===========================================================
# Tao site va dang ky cac tai nguyen
# ===========================================================
def build_site() -> resource.Site:
    site = resource.Site()

    # Dang ky tai nguyen cho tung thiet bi
    for dev_id in DEVICES:
        dev_resource = SmartDeviceResource(dev_id)
        site.add_resource(("iot", "lab", dev_id, "status"), dev_resource)
        logger.info("Resource registered: /iot/lab/%s/status", dev_id)

    # Them well-known/core de ho tro CoAP discovery
    site.add_resource(
        (".well-known", "core"),
        resource.WKCResource(site.get_resources_as_linkheader),
    )
    return site


# ===========================================================
# Diem khoi chay chinh
# ===========================================================
async def main():
    site = build_site()

    # Tren Windows, aiocoap dung transport "simplesocketserver" -> KHONG cho bind
    # any-address ("0.0.0.0" / "::"). Phai bind vao dia chi cu the.
    # Controller va monitor ket noi toi 127.0.0.1 nen bind vao do.
    try:
        await aiocoap.Context.create_server_context(site, bind=("127.0.0.1", 5683))
    except OSError as e:
        raise SystemExit(
            f"Khong bind duoc 127.0.0.1:5683 ({e}). "
            "Co the server cu dang chay: netstat -ano | findstr 5683"
        )

    print("=" * 55)
    print("  CoAP Smart Light Server started on port 5683")
    print("=" * 55)
    for dev_id, info in DEVICES.items():
        print(f"  Resource: coap://127.0.0.1:5683/iot/lab/{dev_id}/status")
        print(f"           ({info['description']})")
    print("=" * 55)
    print(f"  State log file: {LOG_FILE}")
    print("  Nhan Ctrl+C de dung server.")
    print("=" * 55)

    # Chay mai mai cho den khi bi ngat
    await asyncio.get_event_loop().create_future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer da dung.")
