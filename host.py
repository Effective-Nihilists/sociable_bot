import os
import time
import asyncio
from typing import Optional
import uvicorn
import requests
import json
import uuid
from subprocess import Popen
from fastapi import FastAPI, Request
from websockets.asyncio.client import connect, ClientConnection
from apscheduler.schedulers.background import BackgroundScheduler


class Bot:
    def __init__(
        self,
        process: Popen,
        port: int,
        websocket: ClientConnection,
        last_message: float,
    ):
        self.process = process
        self.port = port
        self.websocket = websocket
        self.last_message = last_message


port = os.environ.get("PORT", 6000)
app_url = os.environ.get("APP_URL", "http://localhost:3000")
app_key = "567686a8-6fa1-4c34-88dc-4550154bbab7"

bots: dict[str, Bot] = {}
ports: dict[str, bool] = {}
bot_start_port = 7000
bot_port = bot_start_port

app = FastAPI()


@app.get("/")
def ping():
    return "PONG"


@app.post("/bot/{bot_id}/{updated}")
async def bot(bot_id: str, updated: str, conversation_id: str, request: Request):
    return await bot_everything(
        bot_id=bot_id,
        updated=updated,
        conversation_id=None,
        conversation_thread_id=None,
        request=request,
    )


@app.post("/bot/{bot_id}/{updated}/{conversation_id}")
async def bot_conversation(
    bot_id: str, updated: str, conversation_id: str, request: Request
):
    return await bot_everything(
        bot_id=bot_id,
        updated=updated,
        conversation_id=conversation_id,
        conversation_thread_id=None,
        request=request,
    )


@app.post("/bot/{bot_id}/{updated}/{conversation_id}/{conversation_thread_id}")
async def bot_everything(
    bot_id: str,
    updated: str,
    conversation_id: Optional[str],
    conversation_thread_id: Optional[str],
    request: Request,
):
    global bot_port, ports, bots

    body = await request.body()
    print("BODY", body)
    key = f"{bot_id}-{updated}-{conversation_id}-{conversation_thread_id}"
    bot = bots.get(key)
    if bot is not None and bot.process.poll() is None:
        try:
            bot.last_message = time.time()
            await bot.websocket.send(body)
            return "OK"
        except:
            print(f"[BOT] {key} failed to send command")

    if bot is not None:
        bot.process.kill()
        del bots[key]
        del ports[bot.port]

    # Get bot python code and JWT and bot params
    response = requests.post(
        f"{app_url}/request",
        json={
            "op": "botRunner",
            "input": {
                "secretKey": app_key,
                "botId": bot_id,
                "conversationId": conversation_id,
            },
        },
    )

    output = response.json()
    print("Response:", json.dumps(output, indent=4))

    python_file = f"{str(uuid.uuid4())}.py"
    with open(python_file, "w") as f:
        f.write(output.get("codePython"))

    # Find next available port
    while ports.get(bot_port) is not None:
        bot_port += 1

    port = bot_port
    ports[port] = True

    process = Popen(
        [
            "python",
            python_file,
            str(port),
            output.get("token"),
            json.dumps(
                {
                    "botId": bot_id,
                    "conversationId": conversation_id,
                    "conversationThreadId": conversation_thread_id,
                    "chargeUserIds": output.get("chargeUserIds"),
                    "params": output.get("params"),
                }
            ),
        ]
    )
    start = time.time()
    while True:
        # Fail after 5 seconds
        if time.time() - start > 5:
            os.remove(python_file)
            return "FAILED"

        try:
            async with connect(f"ws://localhost:{port}") as websocket:
                await websocket.send(body)

                bots[key] = Bot(
                    process=process,
                    port=port,
                    websocket=websocket,
                    last_message=time.time(),
                )

                # os.remove(python_file)

                return "OK"
        except:
            await asyncio.sleep(0.1)


def cron():
    now = time.time()
    for key, bot in bots.copy().items():
        # Every 30 seconds remove dead processes
        if bot.process.poll() is not None:
            print(f"[BOT] {key} died")
            del bots[key]
            del ports[bot.port]

        # If no bot message in last 5 minutes then kill the process
        if now - bot.last_message > 5 * 60:
            print(f"[BOT] {key} inactive")
            bot.process.kill()
            del bots[key]
            del ports[bot.port]


sched = BackgroundScheduler()
sched.start()
sched.add_job(cron, "interval", seconds=30)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port)
