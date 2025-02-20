import asyncio
from dataclasses import dataclass
import os
import time
from typing import Optional
import uvicorn
import requests
import json
import uuid
from subprocess import Popen, PIPE
from fastapi import FastAPI, Request
from apscheduler.schedulers.background import BackgroundScheduler


@dataclass
class Bot:
    process: Popen
    last_message: float
    python_file: str


port = os.environ.get("PORT", 6000)
app_host = os.environ.get("APP_HOST", "localhost:3000")
app_key = "567686a8-6fa1-4c34-88dc-4550154bbab7"

print("STARTING", port, __name__, app_host)

bots: dict[str, Bot] = {}

app = FastAPI()


@app.get("/")
def ping():
    return "PONG"


@app.post("/bot/{bot_id}/{updated}")
async def bot(bot_id: str, updated: str, request: Request):
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
    global bots

    body = await request.body()
    key = f"{bot_id}-{updated}-{conversation_id}-{conversation_thread_id}"
    bot = bots.get(key)
    if bot is not None and bot.process.poll() is None:
        try:
            bot.last_message = time.time()
            bot.process.stdin.write(body)
            bot.process.stdin.write(b"\n")
            return "OK"
        except Exception as e:
            print(f"[BOT] {key} failed to send command", e)

    if bot is not None:
        bot.process.kill()
        os.remove(bot.python_file)
        del bots[key]

    # Get bot python code and JWT and bot params
    response = requests.post(
        f"http://{app_host}/request",
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
    # print("Response:", json.dumps(output, indent=4))

    python_file = f"{str(uuid.uuid4())}.py"
    with open(python_file, "w") as f:
        f.write(output.get("codePython"))

    process = Popen(
        [
            "python",
            python_file,
            output.get("token"),
            json.dumps(
                {
                    "botId": bot_id,
                    "botCodeId": output.get("botCodeId"),
                    "conversationId": conversation_id,
                    "conversationThreadId": conversation_thread_id,
                    "chargeUserIds": output.get("chargeUserIds"),
                    "params": output.get("params"),
                }
            ),
        ],
        bufsize=0,
        stdin=PIPE,
        stderr=PIPE,
    )

    def send_error_log():
        line = process.stderr.readline().decode()
        if len(line) > 0:
            print("[ERROR]", line)
            requests.post(
                f"http://{app_host}/request",
                json={
                    "op": "botCodeLog",
                    "input": {
                        "context": {
                            "botId": bot_id,
                            "botCodeId": output.get("botCodeId"),
                            "conversationId": conversation_id,
                            "conversationThreadId": conversation_thread_id,
                            "chargeUserIds": output.get("chargeUserIds"),
                        },
                        "params": {"type": "error", "args": [line]},
                    },
                },
            )

    asyncio.get_event_loop().add_reader(process.stderr, send_error_log)

    process.stdin.write(body)
    process.stdin.write(b"\n")

    bots[key] = Bot(process=process, last_message=time.time(), python_file=python_file)

    return "OK"


def cron():
    now = time.time()
    for key, bot in bots.copy().items():
        # Every 30 seconds remove dead processes
        if bot.process.poll() is not None:
            print(f"[BOT] {key} died")
            os.remove(bot.python_file)
            del bots[key]

        # If no bot message in last 5 minutes then kill the process
        if now - bot.last_message > 5 * 60:
            print(f"[BOT] {key} inactive")
            bot.process.kill()
            os.remove(bot.python_file)
            del bots[key]


sched = BackgroundScheduler()
sched.start()
sched.add_job(cron, "interval", seconds=30)

print("uvicorn start")
try:
    if __name__ == "__main__":
        uvicorn.run("host:app", host="0.0.0.0", port=port)
except Exception as e:
    print(e.message)
