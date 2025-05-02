import asyncio
from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyAIOatLYjf5YExfXOfdlfZwbx2VF3Tiabs")
model = "gemini-2.0-flash-live-001"

config = {"response_modalities": ["TEXT"]}

async def main():
    async with client.aio.live.connect(model=model, config=config) as session:
        while True:
            message = input("User> ")
            if message.lower() == "exit":
                break
            await session.send_client_content(
                turns={"role": "user", "parts": [{"text": message}]}, turn_complete=True
            )

            async for response in session.receive():
                if response.text is not None:
                    print(response.text, end="")


config = {
    "system_instruction": types.Content(
        parts=[
            types.Part(
                text="You are a helpful Working at MCCIA - Mahratta Chamber of Commerce Industries and Agriculture  as  a Consultant and you have to respond to queries of the member MSME's (Medium and Small Scale Companies) in the best way possible while being straight to the Point, Do not give long answers at all ask after each step and then procedd in small text formats "
            )
        ]
    ),
    "response_modalities": ["TEXT"],
}
if __name__ == "__main__":
    asyncio.run(main())