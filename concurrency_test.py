import asyncio
import httpx

URL = "http://127.0.0.1:8000/bookings/"

async def make_booking(client, user_id):
    data = {
        "user_id": user_id,
        "train_id": 3,
        "journey_date": "2026-11-15",
        "number_of_seats": 1
    }

    response = await client.post(URL, json=data)

    return {
        "user_id": user_id,
        "status_code": response.status_code,
        "response": response.json()
    }


async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        results = await asyncio.gather(
            make_booking(client, 3),
            make_booking(client, 4),
            return_exceptions=True
        )

        for result in results:
            print("\n--------------------")
            print(result)


asyncio.run(main())