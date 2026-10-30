
import asyncio

from aiocoap import Context, Message, GET, POST


SERVER_URI = "coap://127.0.0.1:5683/iot/lab/message"

STUDENT_ID = "B23DCCN001"
FULL_NAME = "Nguyen Van A"


async def send_request(protocol, method, uri, payload=None):
    message = Message(code=method, uri=uri)

    if payload is not None:
        message.payload = payload.encode("utf-8")

    # Giới hạn thời gian chờ để thử nghiệm lỗi kết nối
    try:
        request = protocol.request(message)
        response = await asyncio.wait_for(
            request.response,
            timeout=5
        )
        return response

    except asyncio.TimeoutError:
        print("Loi: Het thoi gian cho phan hoi (timeout).")

    except Exception as exc:
        print(f"Loi khi gui yeu cau: {exc}")

    return None


def display_response(response):
    if response is None:
        return

    print(f"Code: {response.code}")
    print(
        "Payload:",
        response.payload.decode("utf-8", errors="replace")
    )


async def main():
    protocol = await Context.create_client_context()

    try:
        # 1. GET thong diep
        print("\n--- GET request ---")
        response = await send_request(
            protocol, GET, SERVER_URI
        )
        display_response(response)

        # 2. POST nhieu thong diep lien tiep
        print("\n--- Multiple POST requests ---")

        messages = [
            f"Xin chao tu CoAP Client - {STUDENT_ID} - {FULL_NAME}",
            f"Thong diep thu 2 - {STUDENT_ID} - {FULL_NAME}",
            f"Thong diep thu 3 - {STUDENT_ID} - {FULL_NAME}",
        ]

        for message in messages:
            print(f"\nSending: {message}")

            response = await send_request(
                protocol, POST, SERVER_URI, message
            )
            display_response(response)

        # 3. GET lai de kiem tra thong diep moi nhat
        print("\n--- GET latest message ---")
        response = await send_request(
            protocol, GET, SERVER_URI
        )
        display_response(response)

        # 4. Truy cap URI khong ton tai
        print("\n--- Test URI not found ---")
        wrong_uri = (
            "coap://127.0.0.1:5683/iot/lab/unknown"
        )

        response = await send_request(
            protocol, GET, wrong_uri
        )
        display_response(response)

        

    finally:
        await protocol.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
