import asyncio
from dataclasses import dataclass
import os
import subprocess
import time
from typing import Dict, Optional
import uvicorn
import requests
import json
import uuid
from subprocess import Popen, PIPE
from fastapi import FastAPI, Request
from apscheduler.schedulers.background import BackgroundScheduler
import shutil


@dataclass
class Bot:
    process: Popen
    last_message: float
    path: str


port = int(os.environ.get("PORT", 6000))
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
        shutil.rmtree(bot.path, ignore_errors=True)
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

    bot_path = f"/tmp/{str(uuid.uuid4())}"
    print("[BOT] path", bot_path)
    source_export(output.get("source"), bot_path)
    pip_install(bot_path)

    process = Popen(
        [
            f"{bot_path}/venv/bin/python",
            "main.py",
            "bot",
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
        cwd=bot_path,
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

    bots[key] = Bot(process=process, last_message=time.time(), path=bot_path)

    return "OK"


def source_export(source: dict[str, dict], path: str):
    os.mkdir(path)
    for key, value in source.items():
        if "text" in value:
            with open(f"{path}/{key}", "w") as f:
                f.write(value["text"])
        else:
            source_export(value, f"{path}/{key}")


def pip_install(path: str):
    subprocess.call(["python", "-m", "venv", f"{path}/venv"])
    subprocess.call(
        [f"{path}/venv/bin/python", "-m", "pip", "install", "-r", "requirements.txt"],
        cwd=path,
    )


def cron():
    now = time.time()
    for key, bot in bots.copy().items():
        # Every 30 seconds remove dead processes
        if bot.process.poll() is not None:
            print(f"[BOT] {key} died")
            shutil.rmtree(bot.path, ignore_errors=True)
            del bots[key]

        # If no bot message in last 5 minutes then kill the process
        if now - bot.last_message > 5 * 60:
            print(f"[BOT] {key} inactive")
            bot.process.kill()
            shutil.rmtree(bot.path, ignore_errors=True)
            del bots[key]


if __name__ == "__main__":
    print("Starting background scheduler")
    sched = BackgroundScheduler()
    sched.start()
    sched.add_job(cron, "interval", seconds=30)

    print("Starting uvicorn")
    uvicorn.run("host:app", host="0.0.0.0", port=port)
