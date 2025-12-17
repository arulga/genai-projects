import asyncio
import websockets

async def test_livekit():
    try:
        print("Testing WebSocket connection to ws://127.0.0.1:7880...")
        async with websockets.connect("ws://127.0.0.1:7880") as websocket:
            print("✅ WebSocket connected successfully!")
            # Send a simple message
            await websocket.send("ping")
            response = await websocket.recv()
            print(f"Received response: {response}")
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(test_livekit())
