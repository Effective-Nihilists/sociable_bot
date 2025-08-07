import asyncio
import json
import os
import select
import shutil
import socket
import subprocess
import time
import uuid
from collections.abc import Generator
from contextlib import closing
from dataclasses import dataclass
from subprocess import PIPE, Popen
from typing import Optional

import httpx
import requests
import uvicorn
from fastapi import FastAPI, Request, Response, WebSocket
from fastapi_proxy_lib.core.http import ReverseHttpProxy
from fastapi_proxy_lib.core.websocket import ReverseWebSocketProxy
from fastapi_utils.tasks import repeat_every
from httpx import AsyncClient
from starlette.requests import Request
from starlette.responses import HTMLResponse


@dataclass
class BotContainer:
    path: str
    instance_count: int


@dataclass
class BotInstance:
    process: Popen
    last_message: float
    port: int
    bot_container_key: str


host_port = int(os.environ.get("PORT", 8000))
app_host = os.environ.get("APP_HOST", "localhost:3000")
app_key = os.environ.get("APP_KEY", "567686a8-6fa1-4c34-88dc-4550154bbab7")
proxy_scheme = os.environ.get("PROXY_SCHEME", "http")
proxy_host = os.environ.get("PROXY_HOST", "localhost:8000")

print("STARTING", host_port, __name__, app_host)

bot_instances: dict[str, BotInstance] = {}
bot_containers: dict[str, BotContainer] = {}

app = FastAPI()


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
    body = (await request.body()).decode()

    bot_instance = await bot_instance_get(
        bot_id=bot_id,
        updated=updated,
        conversation_id=conversation_id,
        conversation_thread_id=conversation_thread_id,
    )

    if bot_instance is not None and bot_instance.process.stdin is not None:
        bot_instance.process.stdin.write(body)
        bot_instance.process.stdin.write("\n")

    return "OK"


async def bot_instance_get(
    bot_id: str,
    updated: str,
    conversation_id: Optional[str],
    conversation_thread_id: Optional[str],
) -> Optional[BotInstance]:
    global bot_instances, bot_containers

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
    bot_code_id = output.get("botCodeId")
    bot_code_updated = output.get("botCodeUpdated")
    # print("Response:", json.dumps(output, indent=4))

    bot_container_key = f"{bot_code_id}-{bot_code_updated}"
    bot_instance_key = f"{bot_id}-{updated}-{conversation_id}-{conversation_thread_id}"
    bot_instance = bot_instances.get(bot_instance_key)
    if bot_instance is not None and bot_instance.process.poll() is None:
        try:
            bot_instance.last_message = time.time()
            return bot_instance
        except Exception as e:
            print(f"[BOT] {bot_instance_key} failed to send command", e)

    if bot_instance is not None:
        bot_instance_kill(bot_instance_key)

    bot_container = bot_containers.get(bot_container_key)
    if bot_container is None:
        bot_container_path = f"/tmp/{str(uuid.uuid4())}"
        print("[BOT] path", bot_container_path)
        source_export(output.get("source"), bot_container_path)
        pip_log = pip_install(bot_container_path)
        requests.post(
            f"http://{app_host}/request",
            json={
                "op": "botCodeLog",
                "input": {
                    "context": {
                        "botId": bot_id,
                        "botCodeId": bot_code_id,
                        "conversationId": conversation_id,
                        "conversationThreadId": conversation_thread_id,
                        "chargeUserIds": output.get("chargeUserIds"),
                    },
                    "params": {"type": "log", "args": ["[BOT] install", pip_log]},
                },
            },
        )

        bot_container = BotContainer(path=bot_container_path, instance_count=0)
        bot_containers[bot_container_key] = bot_container

    bot_instance_port = find_available_port()

    args = [
        f"{bot_container.path}/venv/bin/python",
        "-u",
        "main.py",
        "bot",
        str(bot_instance_port),
        output.get("token"),
        json.dumps(
            {
                "botId": bot_id,
                "botCodeId": bot_code_id,
                "conversationId": conversation_id,
                "conversationThreadId": conversation_thread_id,
                "chargeUserIds": output.get("chargeUserIds"),
                "params": output.get("params"),
            }
        ),
    ]

    print("[BOT] args", args)

    process = Popen(
        args,
        bufsize=1,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        cwd=bot_container.path,
        text=True,
    )

    context = {
        "botId": bot_id,
        "botCodeId": bot_code_id,
        "conversationId": conversation_id,
        "conversationThreadId": conversation_thread_id,
        "chargeUserIds": output.get("chargeUserIds"),
    }

    if process.stderr is not None:
        asyncio.get_event_loop().add_reader(
            process.stderr, send_log, process.stderr, "error", context
        )

    if process.stdout is None:
        raise Exception("[BOT] has no stdout")

    poll_obj = select.poll()
    poll_obj.register(process.stdout, select.POLLIN)

    initialized = False
    start_time = time.time()
    while not initialized:
        poll_result = poll_obj.poll(0)
        if poll_result:
            line = process.stdout.readline()
            if len(line) == 0:
                log(context, "error", ["[BOT] died before initialized"])
                return None

            if line == "[BOT] initialized\n":
                initialized = True

            log(context, "log", [line])

        if time.time() - start_time > 3 * 60:
            log(context, "error", ["[BOT] initialization timed out after 3 minutes"])
            return None

        await asyncio.sleep(0.1)

    if process.stdout is not None:
        asyncio.get_event_loop().add_reader(
            process.stdout, send_log, process.stdout, "log", context
        )

    bot_instance = BotInstance(
        process=process,
        last_message=time.time(),
        bot_container_key=bot_container_key,
        port=bot_instance_port,
    )

    bot_instances[bot_instance_key] = bot_instance

    bot_container.instance_count += 1

    return bot_instance


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
    global bot_instances
    now = time.time()
    for key, bot_instance in bot_instances.copy().items():
        # Every 30 seconds remove dead processes
        if bot_instance.process.poll() is not None:
            print(f"[BOT] {key} died")
            bot_instance_kill(key)

        # If no bot message in last 5 minutes then kill the process
        if now - bot_instance.last_message > 5 * 60:
            print(f"[BOT] {key} inactive")
            bot_instance_kill(key)


def bot_instance_kill(key: str):
    global bot_instances, bot_containers

    bot_instance = bot_instances[key]
    bot_instance.process.kill()
    del bot_instances[key]

    bot_container = bot_containers.get(bot_instance.bot_container_key)
    if bot_container is not None:
        bot_container.instance_count -= 1
        if bot_container.instance_count <= 0:
            shutil.rmtree(bot_container.path, ignore_errors=True)
            del bot_containers[bot_instance.bot_container_key]


def send_log(pipe, type, context):
    line = pipe.readline()
    if len(line) == 0:
        # print("[READER] done and empty")
        asyncio.get_event_loop().remove_reader(pipe)
        return

    log(context, type, [line])


def find_available_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("", 0))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock.getsockname()[1]


@app.get("/proxy")
async def proxy(
    bot_id: str,
    updated: str,
    conversation_id: Optional[str] = None,
    conversation_thread_id: Optional[str] = None,
    url: Optional[str] = None,
    session: Optional[str] = None,
):
    # get bot port
    await bot_instance_get(
        bot_id=bot_id,
        updated=updated,
        conversation_id=conversation_id,
        conversation_thread_id=conversation_thread_id,
    )

    # Use a javascript redirect because iOS safari
    # does not support setting cookies on a redirect
    url = f"{url if url is not None else '/'}"
    response = HTMLResponse(
        f"""
<html>
<body>
<script>
    {f'document.cookie="heroku-session-affinity={session}; path=/; SameSite=None; Secure";' if session is not None else ""}
    window.location="{url}"
</script>
</body>
</html>
"""
    )
    response.set_cookie(key="bot_id", value=bot_id, samesite="none", secure=True)
    response.set_cookie(key="updated", value=updated, samesite="none", secure=True)
    if conversation_id is not None:
        response.set_cookie(
            key="conversation_id", value=conversation_id, samesite="none", secure=True
        )
    if conversation_thread_id is not None:
        response.set_cookie(
            key="conversation_thread_id",
            value=conversation_thread_id,
            samesite="none",
            secure=True,
        )

    return response


class FixOrigin(httpx.Auth):
    def __init__(self, url: str):
        self.url = url

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers["origin"] = self.url
        request.headers["Host"] = "python.ugly.bot"
        request.headers["X-Forwarded-Host"] = proxy_host
        request.headers["X-Forwarded-Proto"] = proxy_scheme
        yield request


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def http_proxy(request: Request, path: str = ""):
    print("[PROXY] http cookies", request.cookies)

    bot_id = request.cookies["bot_id"]
    updated = request.cookies["updated"]
    conversation_id = request.cookies.get("conversation_id")
    conversation_thread_id = request.cookies.get("conversation_thread_id")

    bot_instance = await bot_instance_get(
        bot_id=bot_id,
        updated=updated,
        conversation_id=conversation_id,
        conversation_thread_id=conversation_thread_id,
    )

    if bot_instance is None:
        return

    base_url = f"http://localhost:{bot_instance.port}/"

    proxy = ReverseHttpProxy(
        AsyncClient(auth=FixOrigin(url=base_url)), base_url=base_url
    )
    return await proxy.proxy(request=request, path=path)


@app.websocket("/{path:path}")
async def websocket_proxy(websocket: WebSocket, path: str = ""):
    print("[PROXY] websocket cookies", websocket.cookies)

    bot_id = websocket.cookies["bot_id"]
    updated = websocket.cookies["updated"]
    conversation_id = websocket.cookies.get("conversation_id")
    conversation_thread_id = websocket.cookies.get("conversation_thread_id")

    bot_instance = await bot_instance_get(
        bot_id=bot_id,
        updated=updated,
        conversation_id=conversation_id,
        conversation_thread_id=conversation_thread_id,
    )

    if bot_instance is None:
        return

    base_url = f"http://localhost:{bot_instance.port}/"

    proxy = ReverseWebSocketProxy(
        AsyncClient(auth=FixOrigin(url=base_url)),
        base_url=base_url,
    )
    return await proxy.proxy(websocket=websocket, path=path)


def log(context: dict, type: str, args: list[str]):
    global app_host

    requests.post(
        f"http://{app_host}/request",
        json={
            "op": "botCodeLog",
            "input": {
                "context": context,
                "params": {"type": type, "args": args},
            },
        },
    )


if __name__ == "__main__":
    print("Starting uvicorn")
    uvicorn.run("host:app", host="0.0.0.0", port=host_port)
    print("DONE")
