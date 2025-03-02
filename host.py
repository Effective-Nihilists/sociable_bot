import asyncio
from dataclasses import dataclass
import os
import subprocess
import time
from typing import Optional
import uvicorn
import requests
import json
import uuid
from subprocess import Popen, PIPE
from fastapi import FastAPI, Request
import shutil
from fastapi_utils.tasks import repeat_every
import threading


@dataclass
class Bot:
    process: Popen
    last_message: float
    path: str
    stdout_thread: threading.Thread
    stderr_thread: threading.Thread


port = int(os.environ.get("PORT", 6000))
app_host = os.environ.get("APP_HOST", "localhost:3000")
app_key = os.environ.get("APP_KEY", "567686a8-6fa1-4c34-88dc-4550154bbab7")

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

    body = (await request.body()).decode()
    key = f"{bot_id}-{updated}-{conversation_id}-{conversation_thread_id}"
    bot = bots.get(key)
    if bot is not None and bot.process.poll() is None:
        try:
            bot.last_message = time.time()
            bot.process.stdin.write(body)
            bot.process.stdin.write("\n")
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
    pip_log = pip_install(bot_path)
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
                "params": {"type": "log", "args": ["[BOT] install", pip_log]},
            },
        },
    )

    process = Popen(
        [
            f"{bot_path}/venv/bin/python",
            "-u",
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
        bufsize=1,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        cwd=bot_path,
        text=True,
    )

    def output_reader(process, pipe, type):
        print("[READER] started", pipe, process, pipe)
        with pipe:
            while process.poll() is None:
                line = pipe.readline()
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
                            "params": {"type": type, "args": [line]},
                        },
                    },
                )
        print("[READER] finished", process, pipe)

    # Create reader threads for stdout and stderr
    stdout_thread = threading.Thread(
        target=output_reader, args=(process, process.stdout, "log")
    )
    stderr_thread = threading.Thread(
        target=output_reader, args=(process, process.stderr, "error")
    )

    # # Start the threads
    stdout_thread.start()
    stderr_thread.start()

    process.stdin.write(body)
    process.stdin.write("\n")

    bots[key] = Bot(
        process=process,
        last_message=time.time(),
        path=bot_path,
        stdout_thread=stdout_thread,
        stderr_thread=stderr_thread,
    )

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
    process = subprocess.run(
        ["python", "-m", "venv", f"{path}/venv"], capture_output=True
    )
    error = process.stderr.decode()
    result = process.stdout.decode()
    process = subprocess.run(
        [f"{path}/venv/bin/python", "-m", "pip", "install", "-r", "requirements.txt"],
        capture_output=True,
        cwd=path,
    )
    error += process.stderr.decode()
    result += process.stdout.decode()
    return error + result


@app.on_event("startup")
@repeat_every(seconds=30)
def cron():
    global bots
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
    print("Starting uvicorn")
    uvicorn.run("host:app", host="0.0.0.0", port=port)
