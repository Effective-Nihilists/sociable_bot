from enum import Enum
import os
import asyncio
from typing import Any, Awaitable, Dict, List, Optional, Union
from websockets.asyncio.client import connect, ClientConnection
from websockets.asyncio.server import serve
import sys
import json
import socketio

if len(sys.argv) > 1:
    arguments = sys.argv[1:]
    print("Arguments:", arguments)
else:
    print("No arguments provided.")

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


async def echo(websocket):
    async for message in websocket:
        msg = json.loads(message)
        print(msg)
        func = funcs.get(msg.get("func"))
        if func is not None:
            await func(**msg.get("params"))


async def main():
    print("[BOT] start client socket", app_url)
    await sio.connect(app_url, auth={"token": token})

    async with serve(echo, "localhost", port) as server:
        await asyncio.gather(await sio.wait(), await server.serve_forever())


def bot(message_direct: callable = None):
    global funcs

    funcs["messageDirect"] = message_direct

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


class ImageType(Enum):
    PUBLIC = "public"
    URI = "uri"
    BASE64 = "base64"


class ImagePublic:
    def init(self, uri: str, width: int, height: int, prompt: Optional[str] = None):
        self.type = ImageType.PUBLIC
        self.prompt = prompt
        self.uri = uri
        self.width = width
        self.height = height


class ImageUriResult:
    def init(
        self, uri: Optional[str], width: int, height: int, prompt: Optional[str] = None
    ):
        self.type = ImageType.URI
        self.prompt = prompt
        self.uri = uri
        self.width = width
        self.height = height


class ImageBase64Result:
    def init(self, base64: str, width: int, height: int, prompt: Optional[str] = None):
        self.type = ImageType.BASE64
        self.base64 = base64
        self.prompt = prompt
        self.width = width
        self.height = height


ImageResult = Union[ImageBase64Result, ImageUriResult, ImagePublic]


# JUSTIN: auto-gen enums


class UserLangT:
    pass


class MessageVisibility:
    pass


class MessageColor:
    pass


class Mood:
    pass


class ButtonType:
    pass


class MessageIcon:
    pass


class UserLang:
    pass


class TextGenModel(Enum):
    TOGETHER_MISTRAL_7B = "together_mistral_7b"
    TOGETHER_MIXTRAL_8X7B = "together_mixtral_8x7b"
    TOGETHER_MIXTRAL_8X22B = "together_mixtral_8x22b"
    TOGETHER_META_LLAMA_3_8B = "together_meta_llama_3_8b"
    TOGETHER_META_LLAMA_3_70B = "together_meta_llama_3_70b"
    TOGETHER_META_LLAMA_3_405B = "together_meta_llama_3_405b"
    TOGETHER_META_LLAMA_VISION_3_11B = "together_meta_llama_vision_3_11b"
    TOGETHER_META_LLAMA_VISION_3_90B = "together_meta_llama_vision_3_90b"
    TOGETHER_QWEN2_VISION_72B = "together_qwen2_vision_72b"
    TOGETHER_QWEN2_72B = "together_qwen2_72b"
    TOGETHER_DEEPSEEK_R1 = "together_deepseek_r1"
    TOGETHER_DEEPSEEK_V3 = "together_deepseek_v3"


class Thread:
    def __init__(
        self,
        id: str,
        type: str,
        meetingId: Optional[str] = None,
        messageId: Optional[str] = None,
        sectionId: Optional[str] = None,
    ):
        self.id = id
        self.type = type
        self.meetingId = meetingId
        self.messageId = messageId
        self.sectionId = sectionId


class MessageButtonBase:
    def __init__(self, type: str):
        self.type = type


class MessageButtonLink(MessageButtonBase):
    def __init__(self, icon: MessageIcon, text: str, uri: str):
        super().__init__("link")
        self.icon = icon
        self.text = text
        self.uri = uri


class MessageButtonText(MessageButtonBase):
    def __init__(self, text: str, lang: Optional[UserLangT] = None):
        super().__init__("text")
        self.lang = lang
        self.text = text


class MessageButtonNormal(MessageButtonBase):
    def __init__(
        self,
        text: str,
        func: str,
        params: Optional[Dict[str, Any]] = None,
        buttonType: Optional[ButtonType] = None,
    ):
        super().__init__("button")
        self.text = text
        self.func = func
        self.params = params
        self.buttonType = buttonType


MessageButton = Union[MessageButtonNormal, MessageButtonText, MessageButtonLink]


class CodeMessage:
    def __init__(
        self,
        id: str,
        created: int,
        userId: str,
        text: str,
        isBot: bool,
        markdown: Optional[str] = None,
        system: Optional[bool] = None,
        mentionUserIds: Optional[List[str]] = None,
        lang: Optional[UserLangT] = None,
        onlyUserIds: Optional[List[str]] = None,
        visibility: Optional[MessageVisibility] = None,
        color: Optional[MessageColor] = None,
        cacheTextToSpeech: Optional[bool] = None,
        buttons: Optional[List[MessageButton]] = None,
        mood: Optional[Mood] = None,
        impersonateUserId: Optional[str] = None,
        fileIds: Optional[List[str]] = None,
        contextFileId: Optional[str] = None,
        thread: Optional[Thread] = None,
    ):
        self.id = id
        self.created = created
        self.userId = userId
        self.text = text
        self.markdown = markdown
        self.system = system
        self.mentionUserIds = mentionUserIds
        self.lang = lang
        self.onlyUserIds = onlyUserIds
        self.visibility = visibility
        self.color = color
        self.isBot = isBot
        self.cacheTextToSpeech = cacheTextToSpeech
        self.buttons = buttons
        self.mood = mood
        self.impersonateUserId = impersonateUserId
        self.fileIds = fileIds
        self.contextFileId = contextFileId
        self.thread = thread


CodeTextGenMessageContent = Union[str, ImageUriResult, ImageBase64Result]


class CodeTextGenRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"


class CodeTextGenMessage:
    def __init__(
        self,
        role: CodeTextGenRole,
        content: Union[str, List[CodeTextGenMessageContent]],
    ):
        self.role = role
        self.content = content


class CodeTextGenTool:
    def __init__(self, name: str, description: str, parameters: Dict[str, Any] = None):
        self.name = name
        self.description = description
        self.parameters = parameters


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
