from dataclasses import asdict, is_dataclass
import os
from typing import Any, Callable, Dict, List, Optional, Union
import sys
import json
import socketio
from .bot_types import *
import re
import typing

# if len(sys.argv) > 1:
#     arguments = sys.argv[1:]
#     print("Arguments:", arguments)
# else:
#     print("No arguments provided.")

app_host = os.environ.get("APP_HOST", "localhost:3000")
token = sys.argv[1]
json_data = json.loads(sys.argv[2])
params = json_data.get("params")
sio = socketio.Client()
context = {
    "botId": json_data["botId"],
    "botCodeId": json_data["botCodeId"],
    "conversationId": json_data["conversationId"],
    "conversationThreadId": json_data["conversationThreadId"],
    "chargeUserIds": json_data["chargeUserIds"],
}


@sio.event
def connect():
    old_print("[BOT] connection established")


@sio.event
def disconnect():
    old_print("[BOT] disconnected from server")


@sio.event
def callback(msg):
    funcName = msg.get("func")
    funcParams = msg.get("params")
    func = funcs.get(funcName)
    if func is not None:
        return func(**funcParams)
    else:
        return None


def message_direct_arg_map(dict: Dict[Any, Any]):
    return {"message": Message(**dict["message"])}


arg_map: Dict[str, Callable[[Dict[Any, Any]], Dict[Any, Any]]] = {
    "messageDirect": message_direct_arg_map,
    # "message_add": "messageAdd",
    # "bot_hourly": "botHourly",
    # "file_create": "fileCreate",
    # "conversation_hourly": "conversationHourly",
    # "conversation_start": "conversationStart",
    # "conversation_user_add": "conversationUserAdd",
    # "meeting_start": "meetingStart",
    # "meeting_stop": "meetingStop",
    # "meeting_user_visible": "meetingUserVisible",
    # "thread_stop": "threadStop",
    # "input_changed": "inputChanged",
    # "webpageUpdated": webpage_updated_arg_map,
}


def convert_keys_to_snake_case(data):
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            new_key = re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()
            new_data[new_key] = convert_keys_to_snake_case(value)
        return new_data
    elif isinstance(data, list):
        return [convert_keys_to_snake_case(item) for item in data]
    else:
        return data


def to_camel_case(snake_str):
    return "".join(x.capitalize() for x in snake_str.lower().split("_"))


def to_lower_camel_case(snake_str):
    # We capitalize the first letter of each component except the first one
    # with the 'capitalize' method and join them together.
    camel_string = to_camel_case(snake_str)
    return snake_str[0].lower() + camel_string[1:]


def convert_keys_to_camel_case(data):
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            new_key = to_lower_camel_case(key)
            new_data[new_key] = convert_keys_to_snake_case(value)
        return new_data
    elif isinstance(data, list):
        return [convert_keys_to_snake_case(item) for item in data]
    else:
        return data


def start():
    old_print("[BOT] start client socket", app_host)
    sio.connect(f"ws://{app_host}/", auth={"token": token}, retry=True)
    while True:
        message = sys.stdin.readline()[:-1]
        if len(message) > 0:
            old_print("[BOT] message", message)
            msg = typing.cast(Any, convert_keys_to_snake_case(json.loads(message)))
            funcName = msg.get("func")
            funcParams = msg.get("params")
            func = funcs.get(funcName)
            if func is not None:
                arg_mapper = arg_map.get(funcName)
                if arg_mapper is not None:
                    func(**arg_mapper(funcParams))
                else:
                    func(**funcParams)


def call(op: str, params: dict) -> Any:
    old_print("[BOT] client socket send", op, context, params)
    result = sio.call(
        "call",
        {
            "op": op,
            "input": {
                "context": context,
                "params": convert_keys_to_camel_case(params),
            },
        },
    )
    # print("[BOT] client socket send result", result)
    return (
        convert_keys_to_snake_case(result.get("data")) if result is not None else None
    )


def conversation(id: str) -> Optional[Conversation]:
    result = call(
        "botCodeConversationGet",
        {
            "id": id,
        },
    )
    return Conversation(**result) if result is not None else None


def user(id: str) -> Optional[User]:
    result = call(
        "botCodeUserGet",
        {
            "id": id,
        },
    )
    return User(**result) if result is not None else None


def user_private(id: str) -> Optional[UserPrivate]:
    result = call(
        "botCodeUserPrivateGet",
        {
            "id": id,
        },
    )
    return UserPrivate(**result) if result is not None else None


def live_user(id: str) -> Optional[LiveUser]:
    result = call(
        "botCodeLiveUserGet",
        {
            "id": id,
        },
    )
    return LiveUser(**result) if result is not None else None


def bot(id: str) -> Optional[Bot]:
    result = call(
        "botCodeBotGet",
        {
            "id": id,
        },
    )
    return Bot(**result) if result is not None else None


def bot_owners(id: str) -> List[str]:
    return call(
        "botCodeBotOwnersGet",
        {"id": id},
    )


def message_typing() -> None:
    call(
        "botCodeMessageTyping",
        {},
    )


def message_send(
    id: Optional[str] = None,
    text: Optional[str] = None,
    images: Optional[List[Union[ImageBase64Result, ImageUriResult, None]]] = None,
    markdown: Optional[str] = None,
    mention_user_ids: Optional[List[str]] = None,
    only_user_ids: Optional[List[str]] = None,
    lang: Optional[UserLang] = None,
    visibility: Optional[MessageVisibility] = None,
    color: Optional[MessageColor] = None,
    buttons: Optional[List[MessageButton]] = None,
    mood: Optional[Mood] = None,
    impersonate_user_id: Optional[str] = None,
    files: Optional[List[File]] = None,
    thread: Optional[Thread] = None,
) -> Message:
    return Message(
        **call(
            "botCodeMessageSend",
            {
                "id": id,
                "text": text,
                "markdown": markdown,
                "images": images,
                "mentionUserIds": mention_user_ids,
                "onlyUserIds": only_user_ids,
                "lang": lang,
                "visibility": visibility,
                "color": color,
                "buttons": buttons,
                "mood": mood,
                "impersonateUserId": impersonate_user_id,
                "fileIds": files,
                "thread": thread,
            },
        )
    )


def message_edit(
    id: str, text: Optional[str] = None, markdown: Optional[str] = None
) -> Message:
    return Message(
        **call(
            "botCodeMessageEdit",
            {
                "id": id,
                "text": text,
                "markdown": markdown,
            },
        )
    )


def messages_to_text(
    messages: List[Message], strip_names: Optional[bool] = None
) -> str:
    return call(
        "botCodeMessagesToText",
        {
            "messages": messages,
            "stripNames": strip_names,
        },
    )


def message_history(
    duration: Optional[int] = None,
    limit: Optional[int] = None,
    start: Optional[int] = None,
    include_hidden: Optional[bool] = None,
    thread_id: Optional[str] = None,
) -> List[Message]:
    result = call(
        "botCodeMessageHistory",
        {
            "duration": duration,
            "limit": limit,
            "start": start,
            "include_hidden": include_hidden,
            "thread_id": thread_id,
        },
    )

    return list(map(lambda m: Message(**m), result))


def text_gen(
    question: Optional[str] = None,
    instruction: Optional[str] = None,
    messages: Optional[List[Union[TextGenMessage, Message]]] = None,
    model: Optional[TextGenModel] = None,
    temperature: Optional[float] = None,
    top_k: Optional[int] = None,
    top_p: Optional[float] = None,
    max_tokens: Optional[int] = None,
    frequency_penalty: Optional[float] = None,
    presence_penalty: Optional[float] = None,
    repetition_penalty: Optional[float] = None,
    tools: Optional[List[TextGenTool]] = None,
    include_files: Optional[bool] = None,
    json: Optional[Dict[str, Any]] = None,
) -> str:
    return call(
        "botCodeTextGen",
        {
            "question": question,
            "instruction": instruction,
            "messages": (
                list(map(lambda x: asdict(x), messages))
                if messages is not None
                else None
            ),
            "model": model,
            "temperature": temperature,
            "topK": top_k,
            "topP": top_p,
            "maxTokens": max_tokens,
            "frequencyPenalty": frequency_penalty,
            "presencePenalty": presence_penalty,
            "repetitionPenalty": repetition_penalty,
            "tools": (
                list(map(lambda x: asdict(x), tools)) if tools is not None else None
            ),
            "includeFiles": include_files,
            "json": json,
        },
    )


def query_files(
    query: str,
    scope: Optional[str] = None,
    catalog_ids: Optional[List[str]] = None,
    limit: Optional[int] = None,
) -> List[FileChunk]:
    result = call(
        "botCodeQueryFiles",
        {
            "query": query,
            "scope": scope,
            "catalogIds": catalog_ids,
            "limit": limit,
        },
    )

    return list(map(lambda m: FileChunk(**m), result))


def query_news(
    query: str, created: Optional[int] = None, limit: Optional[int] = None
) -> List[NewsArticle]:
    result = call(
        "botCodeQueryNews",
        {
            "query": query,
            "created": created,
            "limit": limit,
        },
    )

    return list(map(lambda m: NewsArticle(**m), result))


def image_gen(
    prompt: str,
    model: Optional[ImageGenModel] = None,
    negative_prompt: Optional[str] = None,
    size: Optional[ImageGenSize] = None,
    guidance_scale: Optional[float] = None,
    steps: Optional[int] = None,
    image: Optional[ImageResult] = None,
    image_strength: Optional[float] = None,
) -> Optional[ImageBase64Result]:
    result = call(
        "botCodeImageGen",
        {
            "prompt": prompt,
            "model": model,
            "negativePrompt": negative_prompt,
            "size": size,
            "guidanceScale": guidance_scale,
            "steps": steps,
            "image": image,
            "imageStrength": image_strength,
        },
    )
    return ImageBase64Result(**result) if result is not None else None


def google_search(query: str) -> List[SearchArticle]:
    result = call(
        "botCodeGoogleSearch",
        {
            "query": query,
        },
    )

    return list(map(lambda m: SearchArticle(**m), result))


def email_send(
    user_id: Optional[str] = None,
    user_ids: Optional[List[str]] = None,
    subject: Optional[str] = None,
    text: Optional[str] = None,
    markdown: Optional[str] = None,
    file_id: Optional[str] = None,
) -> None:
    call(
        "botCodeEmailSend",
        {
            "userId": user_id,
            "userIds": user_ids,
            "subject": subject,
            "text": text,
            "markdown": markdown,
            "fileId": file_id,
        },
    )


def conversation_users(
    type: Optional[str] = None, role: Optional[str] = None
) -> List[User]:
    result = call(
        "botCodeConversationUsers",
        {"type": type, "role": role},
    )

    return list(map(lambda m: User(**m), result))


def conversation_bots(tag: Optional[BotTag] = None) -> List[Bot]:
    result = call(
        "botCodeConversationBots",
        {
            "tag": tag,
        },
    )

    return list(map(lambda m: Bot(**m), result))


def conversation_show_content(content: ConversationContent) -> None:
    call(
        "botCodeConversationShowContent",
        asdict(content),
    )


def conversation_show_buttons(
    user_id: Optional[str] = None, buttons: Optional[List[MessageButton]] = None
) -> None:
    call(
        "botCodeConversationShowButtons",
        {
            "userId": user_id,
            "buttons": buttons,
        },
    )


def conversation_participants(type: Optional[str] = None) -> List[User]:
    result = call(
        "botCodeConversationParticipants",
        {
            "type": type,
        },
    )

    return list(map(lambda m: User(**m), result))


def file_create(
    type: FileType,
    title: str,
    markdown: Optional[str] = None,
    uri: Optional[str] = None,
    thumbnail: Optional[Union[ImageBase64Result, ImageUriResult]] = None,
    lang: Optional[UserLang] = None,
    indexable: Optional[bool] = None,
    message_send: Optional[bool] = None,
    add_to_conversation: Optional[bool] = None,
    add_to_feed: Optional[bool] = None,
    send_notification: Optional[bool] = None,
) -> File:
    return File(
        **call(
            "botCodeFileCreate",
            {
                "type": type,
                "title": title,
                "markdown": markdown,
                "uri": uri,
                "thumbnail": thumbnail,
                "lang": lang,
                "indexable": indexable,
                "messageSend": message_send,
                "addToConversation": add_to_conversation,
                "addToFeed": add_to_feed,
                "sendNotification": send_notification,
            },
        )
    )


def file_update(
    id: str,
    markdown: Optional[str] = None,
    title: Optional[str] = None,
    thumbnail: Optional[ImageResult] = None,
) -> None:
    call(
        "botCodeFileUpdate",
        {
            "id": id,
            "title": title,
            "markdown": markdown,
            "thumbnail": thumbnail,
        },
    )


def file_to_text_gen_message(
    file: File,
    role: Optional[TextGenRole] = None,
    include_name: Optional[bool] = None,
    text: Optional[str] = None,
) -> TextGenMessage:
    return TextGenMessage(
        **call(
            "botCodeFileToTextGenMessage",
            {
                "file": file,
                "role": role,
                "includeName": include_name,
                "text": text,
            },
        )
    )


def markdown_create_image(
    file_id: str, image: Union[ImageBase64Result, ImageUriResult]
) -> str:
    return call(
        "botCodeMarkdownCreateImage",
        {
            "file_id": file_id,
            "image": image,
        },
    )


def data_set(**kwargs) -> dict:
    return call(
        "botCodeDataSet",
        kwargs,
    )


def data() -> dict:
    return call(
        "botCodeDataGet",
        {},
    )


def bot_search(query: str, limit: Optional[int] = None) -> List[Bot]:
    result = call(
        "botCodeBotSearch",
        {"query": query, "limit": limit},
    )

    return list(map(lambda m: Bot(**m), result))


def web_page_get(session_id: str) -> WebPageData:
    result = call(
        "botCodeWebPageGet",
        {"session_id": session_id},
    )

    return WebPageData(**result)


old_print = print


def log(
    *args: list[Any],
) -> None:
    old_print(args)
    call(
        "botCodeLog",
        {
            "type": "log",
            "args": list(map(lambda x: asdict(x) if is_dataclass(x) else x, args)),
        },
    )


print = log


def error(
    *args: list[Any],
) -> None:
    call(
        "botCodeLog",
        {
            "type": "error",
            "args": list(map(lambda x: asdict(x) if is_dataclass(x) else x, args)),
        },
    )
