import os
import asyncio
from typing import Any, Awaitable, Callable, Dict, List, Optional, Protocol, Union
import sys
import json
import socketio
from bot_types import *

# if len(sys.argv) > 1:
#     arguments = sys.argv[1:]
#     print("Arguments:", arguments)
# else:
#     print("No arguments provided.")

app_url = os.environ.get("APP_WSS", "ws://localhost:3000/")
port = sys.argv[1]
token = sys.argv[2]
data = json.loads(sys.argv[3])
params = data.get("params")
funcs = {}
sio = socketio.AsyncClient()
context = {
    "botId": data["botId"],
    "conversationId": data["conversationId"],
    "conversationThreadId": data["conversationThreadId"],
    "chargeUserIds": data["chargeUserIds"],
    "botCodeRunId": None,
}

print("HI")


@sio.event
async def connect():
    print("connection established")


@sio.event
async def my_message(data):
    print("message received with ", data)
    await sio.emit("my response", {"response": "my response"})


@sio.event
async def disconnect():
    print("disconnected from server")


async def main():
    print("[BOT] start client socket", app_url)
    await sio.connect(app_url, auth={"token": token})
    while True:
        message = sys.stdin.readline()[:-1]
        if len(message) > 0:
            print("[MESSAGE]", message)
            msg = json.loads(message)
            func = funcs.get(msg.get("func"))
            if func is not None:
                await func(**msg.get("params"))


def bot(
    message_direct: Optional[MessageDirectProtocol] = None,
    message_add: Optional[MessageAddProtocol] = None,
    bot_hourly: Optional[BotHourlyProtocol] = None,
    file_create: Optional[FileCreateProtocol] = None,
    conversation_hourly: Optional[ConversationHourlyProtocol] = None,
    conversation_start: Optional[ConversationStartProtocol] = None,
    conversation_user_add: Optional[ConversationUserAddProtocol] = None,
    meeting_start: Optional[MeetingStartProtocol] = None,
    meeting_stop: Optional[MeetingStopProtocol] = None,
    meeting_user_visible: Optional[MeetingUserVisibleProtocol] = None,
    thread_stop: Optional[ThreadStopProtocol] = None,
    input_changed: Optional[InputChangedProtocol] = None,
):
    global funcs

    funcs["messageDirect"] = message_direct
    funcs["messageAdd"] = message_add
    funcs["botHourly"] = bot_hourly
    funcs["fileCreate"] = file_create
    funcs["conversationHourly"] = conversation_hourly
    funcs["conversationStart"] = conversation_start
    funcs["conversationUserAdd"] = conversation_user_add
    funcs["meetingStart"] = meeting_start
    funcs["meetingStop"] = meeting_stop
    funcs["meetingUserVisible"] = meeting_user_visible
    funcs["threadStop"] = thread_stop
    funcs["inputChanged"] = input_changed

    asyncio.run(main())


async def call(op: str, params: dict) -> Awaitable[dict]:
    print("[BOT] client socket send", op, context, params)
    result = await sio.call(
        "call",
        {
            "op": op,
            "input": {
                "context": context,
                "params": params,
            },
        },
    )
    return result.get("data")


async def text_gen(
    question: str = None,
    instruction: str = None,
    messages: List[Union[CodeTextGenMessage | CodeMessage]] = None,
    model: TextGenModel = None,
    temperature: float = None,
    top_k: float = None,
    top_p: float = None,
    max_tokens: int = None,
    frequency_penalty: float = None,
    presence_penalty: float = None,
    repetition_penalty: float = None,
    tools: List[CodeTextGenTool] = None,
    include_files: bool = None,
    json: object = None,
) -> Awaitable[str]:
    return await call(
        "botCodeTextGen",
        {
            "question": question,
            "instruction": instruction,
            "messages": messages,
            "model": model.value if model is not None else None,
            "temperature": temperature,
            "topK": top_k,
            "topP": top_p,
            "maxTokens": max_tokens,
            "frequencyPenalty": frequency_penalty,
            "presencePenalty": presence_penalty,
            "repetitionPenalty": repetition_penalty,
            "tools": tools,
            "includeFiles": include_files,
            "json": json,
        },
    )


async def message_send(
    id: Optional[str] = None,
    text: Optional[str] = None,
    markdown: Optional[str] = None,
    images: Optional[List[Union[ImageResult | None]]] = None,
    mentionUserIds: Optional[List[str]] = None,
    onlyUserIds: Optional[List[str]] = None,
    lang: Optional[UserLang] = None,
    visibility: Optional[MessageVisibility] = None,
    color: Optional[MessageColor] = None,
    buttons: Optional[MessageButton] = None,
    mood: Optional[Mood] = None,
    impersonateUserId: Optional[str] = None,
    fileIds: Optional[List[str]] = None,
    thread: Optional[Thread] = None,
) -> Awaitable[str]:
    return await call(
        "botCodeMessageSend",
        {
            "id": id,
            "text": text,
            "markdown": markdown,
            "images": images,
            "mentionUserIds": mentionUserIds,
            "onlyUserIds": onlyUserIds,
            "lang": lang,
            "visibility": visibility.value if visibility is not None else None,
            "color": color.value if visibility is not None else None,
            "buttons": buttons,
            "mood": mood.value if visibility is not None else None,
            "impersonateUserId": impersonateUserId,
            "fileIds": fileIds,
            "thread": thread,
        },
    )
