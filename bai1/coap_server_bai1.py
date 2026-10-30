
import asyncio
from datetime import datetime

from aiocoap import resource, Context, Message, CONTENT, CHANGED


class MessageResource(resource.Resource):
    def __init__(self):
        super().__init__()
        self.latest_message = None

    async def render_get(self, request):
        print("\nGET request received:")
        print(f"URI: {request.get_request_uri()}")

        if self.latest_message is None:
            response = "Xin chao tu CoAP Server"
        else:
            response = self.latest_message

        return Message(
            code=CONTENT,
            payload=response.encode("utf-8")
        )

    async def render_post(self, request):
        message = request.payload.decode(
            "utf-8", errors="replace"
        )

        received_at = datetime.now().strftime("%H:%M:%S")

        # Lưu thông điệp mới nhất để GET trả về sau đó
        self.latest_message = message

        print("\nPOST request received:")
        print(f"Payload: {message}")
        print(f"Time: {received_at}")

        return Message(
            code=CHANGED,
            payload="Server da nhan thong diep".encode("utf-8")
        )


async def main():
    root = resource.Site()

    root.add_resource(
        ["iot", "lab", "message"],
        MessageResource()
    )

    await Context.create_server_context(
        root,
        bind=("127.0.0.1", 5683)
    )

    print("CoAP Server started on port 5683")
    print("URI: coap://127.0.0.1:5683/iot/lab/message")

    try:
        await asyncio.get_running_loop().create_future()
    finally:
        pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCoAP Server stopped.")
