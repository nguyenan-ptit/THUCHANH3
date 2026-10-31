"""Bai 2: Mo phong cam bien nhiet do va do am bang CoAP."""

import asyncio
from datetime import datetime
import json
import random

from aiocoap import Context, Message, CONTENT, resource


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5683
UPDATE_INTERVAL = 3
SENSOR_IDS = ("sensor01", "sensor02", "sensor03")
TEMPERATURE_RANGE = (20.0, 40.0)
HUMIDITY_RANGE = (30.0, 80.0)


class SensorResource(resource.Resource):
    """GET tra ve mau gan nhat; viec lay mau chay doc lap voi client."""

    def __init__(self, device_id: str):
        super().__init__()
        self.device_id = device_id
        self.data = {}
        self.update_data()

    def update_data(self):
        self.data = {
            "device_id": self.device_id,
            "temperature": round(random.uniform(*TEMPERATURE_RANGE), 1),
            "humidity": round(random.uniform(*HUMIDITY_RANGE), 1),
            "timestamp": datetime.now().isoformat(timespec="milliseconds"),
        }
        print(
            f"[{self.data['timestamp']}] {self.device_id}: "
            f"{self.data['temperature']:.1f} C, "
            f"{self.data['humidity']:.1f} %"
        )

    async def render_get(self, request):
        print(f"GET request received: /iot/lab/{self.device_id}/data")
        return Message(
            code=CONTENT,
            payload=json.dumps(self.data).encode("utf-8"),
            content_format=50,  # application/json, giong bai 3
            max_age=0,  # Client can lay mau moi o moi lan GET.
        )


def build_site():
    site = resource.Site()
    sensors = [SensorResource(device_id) for device_id in SENSOR_IDS]
    for sensor in sensors:
        site.add_resource(("iot", "lab", sensor.device_id, "data"), sensor)
    return site, sensors


async def update_sensors(sensors):
    while True:
        await asyncio.sleep(UPDATE_INTERVAL)
        for sensor in sensors:
            sensor.update_data()


async def main():
    site, sensors = build_site()
    protocol = await Context.create_server_context(
        site, bind=(SERVER_HOST, SERVER_PORT)
    )
    updater = asyncio.create_task(update_sensors(sensors))
    print(f"\nSensor CoAP Server started on port {SERVER_PORT}")
    for device_id in SENSOR_IDS:
        print(
            f"URI: coap://{SERVER_HOST}:{SERVER_PORT}"
            f"/iot/lab/{device_id}/data"
        )
    print(f"Cap nhat cam bien moi {UPDATE_INTERVAL} giay. Nhan Ctrl+C de dung.")

    try:
        await asyncio.get_running_loop().create_future()
    finally:
        updater.cancel()
        await asyncio.gather(updater, return_exceptions=True)
        await protocol.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSensor CoAP Server da dung.")
    except OSError as exc:
        print(f"Khong the khoi tao server: {exc}")
        print("Hay dung server bai 1/bai 3 neu dang su dung cong UDP 5683.")
        raise SystemExit(1)
