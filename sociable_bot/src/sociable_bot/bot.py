import asyncio
import json
import os
import re
import sys
import threading
import typing
from dataclasses import asdict, dataclass, is_dataclass
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional, Union

import socketio

from .bot_types import *

# if len(sys.argv) > 1:
#     arguments = sys.argv[1:]
#     print("Arguments:", arguments)
# else:
#     print("No arguments provided.")


@dataclass
class Call:
    op: str
    params: dict
    case_change: bool


app_host = os.environ.get("APP_HOST", "localhost:3000")
sio = socketio.Client()
bot_port = int(sys.argv[2]) if len(sys.argv) > 1 and sys.argv[1] == "bot" else None
token = sys.argv[3] if len(sys.argv) > 1 and sys.argv[1] == "bot" else None
json_data = (
    json.loads(sys.argv[4]) if len(sys.argv) > 1 and sys.argv[1] == "bot" else None
)
started = False
pending_calls: List[Call] = []

bot_params = SimpleNamespace(**json_data["params"]) if json_data is not None else None
"""Bot Params"""

bot_id = json_data["botId"] if json_data is not None else None
"""Bot ID"""

conversation_id = json_data["conversationId"] if json_data is not None else None
"""Conversation ID"""

thread_id = json_data["conversationThreadId"] if json_data is not None else None
"""Conversation Thread ID"""

bot_context = (
    {
        "botId": json_data["botId"],
        "botCodeId": json_data["botCodeId"],
        "conversationId": json_data["conversationId"],
        "conversationThreadId": json_data["conversationThreadId"],
        "chargeUserIds": json_data["chargeUserIds"],
    }
    if json_data is not None
    else None
)


@sio.event
def connect():
    # print("[BOT] connection established")
    pass


@sio.event
def disconnect():
    # print("[BOT] disconnected from server")
    pass


@sio.event
def callback(msg):
    log("[BOT] function call", msg)
    funcName = msg.get("func")
    funcParams = msg.get("params")
    func = funcs.get(funcName)
    if func is not None:
        return func(**funcParams)
    else:
        return None


def message_arg_map(dict: Dict[Any, Any]):
    return {
        "message": Message(**dict["message"]),
        "conversation": Conversation(**dict["conversation"]),
    }


def conversation_arg_map(dict: Dict[Any, Any]):
    return {
        "conversation": Conversation(**dict["conversation"]),
    }


def conversation_user_arg_map(dict: Dict[Any, Any]):
    return {
        "user": User(**dict["user"]),
        "conversation": Conversation(**dict["conversation"]),
    }


def live_user_visible_arg_map(dict: Dict[Any, Any]):
    return {
        "live_user": LiveUser(**dict["live_user"]),
        "conversation": Conversation(**dict["conversation"]),
    }


def thread_arg_map(dict: Dict[Any, Any]):
    return {
        "thread": Thread(**dict["thread"]),
    }


arg_map: Dict[str, Callable[[Dict[Any, Any]], Dict[Any, Any]]] = {
    "messageDirect": message_arg_map,
    "messageAdd": message_arg_map,
    "conversationStart": conversation_arg_map,
    "conversationUserAdd": conversation_arg_map,
    "userVisible": live_user_visible_arg_map,
    "threadStop": thread_arg_map,
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


def convert_to_dict(data):
    if is_dataclass(data):
        return convert_to_dict(asdict(data))
    elif isinstance(data, SimpleNamespace):
        return convert_to_dict(data.__dict__)
    elif isinstance(data, dict):
        return dict(map(lambda kv: (kv[0], convert_to_dict(kv[1])), data.items()))
    elif isinstance(data, list) or isinstance(data, tuple):
        return list(map(lambda v: convert_to_dict(v), data))
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
            new_data[new_key] = convert_keys_to_camel_case(value)
        return new_data
    elif isinstance(data, list):
        return [convert_keys_to_camel_case(item) for item in data]
    else:
        return data


def start():
    """
    Start your bot, this runs the event loop so your bot can receive calls
    """
    # print("[BOT] start client socket", app_host)
    sio.connect(f"ws://{app_host}/", auth={"token": token}, retry=True)

    print("[BOT] initialized")

    global pending_calls, started
    started = True
    calls = pending_calls
    pending_calls = []
    for call in calls:
        call_no_return(call.op, call.params, call.case_change)

    message_read_loop()


def run_call(message: str):
    msg = typing.cast(Any, convert_keys_to_snake_case(json.loads(message)))
    log("[BOT] message", msg)
    funcName = msg.get("func")
    funcParams = msg.get("params")
    func = funcs.get(funcName)
    if func is not None:
        arg_mapper = arg_map.get(funcName)
        if arg_mapper is not None:
            func(**arg_mapper(funcParams))
        else:
            func(**funcParams)


def start_nonblocking():
    """
    Start your bot, this start an async loop to handle future calls
    """
    sio.connect(f"ws://{app_host}/", auth={"token": token}, retry=True)

    print("[BOT] initialized")

    global pending_calls, started
    started = True
    calls = pending_calls
    pending_calls = []
    for call in calls:
        call_no_return(call.op, call.params, call.case_change)

    thread = threading.Thread(target=message_read_loop)
    thread.start()
    print("[BOT] start done", app_host)


def message_read_loop():
    while True:
        message = sys.stdin.readline()[:-1]
        if len(message) > 0:
            run_call(message)


def call_return(op: str, params: dict, case_change: bool = True) -> Any:
    if not started:
        raise Exception(
            "You cannot call bot functions that require a return value until after start()"
        )

    converted = convert_to_dict(params)
    # print("[BOT] client socket send", op, bot_context, converted)
    result = sio.call(
        "call",
        {
            "op": op,
            "input": {
                "context": bot_context,
                "params": (
                    convert_keys_to_camel_case(converted) if case_change else converted
                ),
            },
        },
    )

    if result is None:
        raise Exception("Invalid response")

    error = result.get("error")
    if error is not None:
        raise Exception(error)

    return (
        convert_keys_to_snake_case(result.get("data"))
        if case_change
        else result.get("data")
    )


def call_no_return(op: str, params: Any, case_change: bool = True) -> None:
    if not started:
        pending_calls.append(Call(op=op, params=params, case_change=case_change))
        return

    converted = convert_to_dict(params)
    # print("[BOT] client socket send", op, bot_context, converted)
    result = sio.call(
        "call",
        {
            "op": op,
            "input": {
                "context": bot_context,
                "params": (
                    convert_keys_to_camel_case(converted) if case_change else converted
                ),
            },
        },
    )

    if result is None:
        raise Exception("Invalid response")

    error = result.get("error")
    if error is not None:
        raise Exception(error)


def conversation_get(id: str) -> Optional[Conversation]:
    """
    Get conversation
    """
    result = call_return(
        "botCodeConversationGet",
        {
            "id": id,
        },
    )
    return Conversation(**result) if result is not None else None


def user_get(id: str) -> Optional[User]:
    """
    Get user
    """
    result = call_return(
        "botCodeUserGet",
        {
            "id": id,
        },
    )
    return User(**result) if result is not None else None


def live_user_get(id: str) -> Optional[LiveUser]:
    """
    Get live user
    """
    result = call_return(
        "botCodeLiveUserGet",
        {
            "id": id,
        },
    )
    return LiveUser(**result) if result is not None else None


def bot_get(id: str) -> Optional[Bot]:
    """
    Get bot
    """
    result = call_return(
        "botCodeBotGet",
        {
            "id": id,
        },
    )
    return Bot(**result) if result is not None else None


def bot_owners_get(id: str) -> List[str]:
    """
    Get owners of a bot
    """
    return call_return(
        "botCodeBotOwnersGet",
        {"id": id},
    )


def file_get(id: str) -> Optional[File]:
    """
    Get file
    """
    result = call_return(
        "botCodeFileGet",
        {
            "id": id,
        },
    )
    return File(**result) if result is not None else None


def message_typing() -> None:
    """
    Show a typing indicator in the active conversation
    """
    call_no_return(
        "botCodeMessageTyping",
        {},
    )


def message_send(
    id: Optional[str] = None,
    text: Optional[str] = None,
    image: Optional[Image] = None,
    images: Optional[List[Image]] = None,
    markdown: Optional[str] = None,
    mention_user_ids: Optional[List[str]] = None,
    only_user_ids: Optional[List[str]] = None,
    lang: Optional[UserLang] = None,
    visibility: Optional[MessageVisibility] = None,
    color: Optional[MessageColor] = None,
    buttons: Optional[List[Button]] = None,
    mood: Optional[Mood] = None,
    impersonate_user_id: Optional[str] = None,
    files: Optional[List[File]] = None,
    thread: Optional[Thread] = None,
) -> Message:
    """
    Send a message to the active conversation
    """
    return Message(
        **call_return(
            "botCodeMessageSend",
            {
                "id": id,
                "text": text,
                "markdown": markdown,
                "image": image,
                "images": images,
                "mention_user_ids": mention_user_ids,
                "only_user_ids": only_user_ids,
                "lang": lang,
                "visibility": visibility,
                "color": color,
                "buttons": buttons,
                "mood": mood,
                "impersonate_user_id": impersonate_user_id,
                "file_ids": [file.id for file in files] if files is not None else None,
                "thread": thread,
            },
        )
    )


def message_post(
    text: Optional[str] = None,
    image: Optional[Image] = None,
    images: Optional[List[Image]] = None,
    markdown: Optional[str] = None,
    lang: Optional[UserLang] = None,
    visibility: Optional[MessageVisibility] = None,
    color: Optional[MessageColor] = None,
    buttons: Optional[List[Button]] = None,
    mood: Optional[Mood] = None,
    files: Optional[List[File]] = None,
) -> None:
    """
    Send a message to the active conversation
    """
    call_no_return(
        "botCodeMessagePost",
        {
            "text": text,
            "markdown": markdown,
            "image": image,
            "images": images,
            "lang": lang,
            "visibility": visibility,
            "color": color,
            "buttons": buttons,
            "mood": mood,
            "file_ids": [file.id for file in files] if files is not None else None,
        },
    )


def message_edit(
    id: str, text: Optional[str] = None, markdown: Optional[str] = None
) -> Message:
    """
    Edit an existing message
    """
    return Message(
        **call_return(
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
    """
    Convert a list of messages into string, useful if you need to add your conversation history to an LLM prompt
    """
    return call_return(
        "botCodeMessagesToText",
        {
            "messages": messages,
            "strip_names": strip_names,
        },
    )


def message_history(
    duration: Optional[int] = None,
    limit: Optional[int] = None,
    start: Optional[int] = None,
    include_hidden: Optional[bool] = None,
    thread_id: Optional[str] = None,
) -> List[Message]:
    """
    Get messages from the active conversation
    """
    result = call_return(
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
) -> Optional[str]:
    """
    Generate text using the specified model (LLM)
    """
    return call_return(
        "botCodeTextGen",
        {
            "question": question,
            "instruction": instruction,
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "repetition_penalty": repetition_penalty,
            "tools": tools,
            "include_files": include_files,
            "json": json,
        },
    )


def query_files(
    query: str,
    scope: Optional[str] = None,
    catalog_ids: Optional[List[str]] = None,
    limit: Optional[int] = None,
) -> List[FileChunk]:
    """
    Get files based on semantic search using the query
    """
    result = call_return(
        "botCodeQueryFiles",
        {
            "query": query,
            "scope": scope,
            "catalog_ids": catalog_ids,
            "limit": limit,
        },
    )

    return list(map(lambda m: FileChunk(**m), result))


def query_news(
    query: str, created: Optional[int] = None, limit: Optional[int] = None
) -> List[NewsArticle]:
    """
    Get news based on semantic search using the query
    """
    result = call_return(
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
    image: Optional[Image] = None,
    image_strength: Optional[float] = None,
) -> Optional[Image]:
    """
    Generate an image using specified model
    """
    result = call_return(
        "botCodeImageGen",
        {
            "prompt": prompt,
            "model": model,
            "negative_prompt": negative_prompt,
            "size": size,
            "guidance_scale": guidance_scale,
            "steps": steps,
            "image": image,
            "image_strength": image_strength,
        },
    )
    return Image(**result) if result is not None else None


def google_search(query: str) -> List[SearchArticle]:
    """
    Google search
    """
    result = call_return(
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
    """
    Send email
    """
    call_no_return(
        "botCodeEmailSend",
        {
            "user_id": user_id,
            "user_ids": user_ids,
            "subject": subject,
            "text": text,
            "markdown": markdown,
            "file_id": file_id,
        },
    )


def conversation_users(
    type: Optional[str] = None, role: Optional[str] = None
) -> List[User]:
    """
    Get users for the active conversation
    """
    result = call_return(
        "botCodeConversationUsers",
        {"type": type, "role": role},
    )

    return list(map(lambda m: User(**m), result))


def conversation_bots(tag: Optional[BotTag] = None) -> List[Bot]:
    """
    Get bots for the active conversation
    """
    result = call_return(
        "botCodeConversationBots",
        {
            "tag": tag,
        },
    )

    return list(map(lambda m: Bot(**m), result))


def conversation_cron_extend(
    end: Optional[int] = None,
) -> None:
    """
    Extends the end of cron jobs for this conversation
    """
    call_no_return(
        "botCodeConversationCronExtend",
        {
            "end": end,
        },
    )


def conversation_content_show(
    type: ConversationContentType = ConversationContentType.URI,
    file_id: Optional[str] = None,
    disabled: Optional[bool] = None,
    uri: Optional[str] = None,
    padding: Optional[Padding] = None,
) -> None:
    """
    Show content in the active conversation
    """
    call_no_return(
        "botCodeConversationContentShow",
        {
            "type": type,
            "file_id": file_id,
            "disabled": disabled,
            "uri": uri,
            "padding": padding,
        },
    )


def conversation_content_hide() -> None:
    """
    Show content in the active conversation
    """
    call_no_return(
        "botCodeConversationContentShow",
        None,
    )


def conversation_content_maximized(
    maximized: bool, user_id: Optional[str] = None
) -> None:
    """
    Toggle the content netween maximized and normal size
    """
    call_no_return(
        "botCodeConversationContentMaximized",
        {"maximized": maximized, "user_id": user_id},
    )


def conversation_buttons_show(
    user_id: Optional[str] = None, buttons: Optional[List[Button]] = None
) -> None:
    """
    Show buttons in the active conversation
    """
    call_no_return(
        "botCodeConversationButtonsShow",
        {
            "user_id": user_id,
            "buttons": buttons,
        },
    )


def tool_context_menu_set(
    user_id: str, menu_items: Optional[List[MenuItem]] = None
) -> None:
    """
    Add context menu to the current web page all of the time
    """
    call_no_return(
        "botCodeToolContextMenuSet",
        {
            "user_id": user_id,
            "menu_items": menu_items,
        },
    )


def tool_conversation_show(
    session_id: str,
    video_call_enabled: Optional[bool] = None,
) -> None:
    """
    Open a conversation
    """
    call_no_return(
        "botCodeToolConversationShow",
        {
            "session_id": session_id,
            "video_call_enabled": video_call_enabled,
        },
    )


def conversation_context_menu_set(
    user_id: Optional[str] = None, menu_items: Optional[List[MenuItem]] = None
) -> None:
    """
    Add context menu to the current web page when this conversation is active
    """
    call_no_return(
        "botCodeConversationContextMenuSet",
        {
            "user_id": user_id,
            "menu_items": menu_items,
        },
    )


def file_create(
    type: FileType,
    title: str,
    markdown: Optional[str] = None,
    uri: Optional[str] = None,
    thumbnail: Optional[Image] = None,
    lang: Optional[UserLang] = None,
    indexable: Optional[bool] = None,
    characters: Optional[Dict[str, Character]] = None,
) -> File:
    """
    Create file
    """
    return File(
        **call_return(
            "botCodeFileCreate",
            {
                "type": type,
                "title": title,
                "markdown": markdown,
                "uri": uri,
                "thumbnail": thumbnail,
                "lang": lang,
                "indexable": indexable,
                "characters": characters,
            },
        )
    )


def file_update(
    id: str,
    markdown: Optional[str] = None,
    title: Optional[str] = None,
    thumbnail: Optional[Image] = None,
) -> None:
    """
    Update file, only supported on markdown files
    """
    call_no_return(
        "botCodeFileUpdate",
        {
            "id": id,
            "title": title,
            "markdown": markdown,
            "thumbnail": thumbnail,
        },
    )


def file_book_character_set(
    file_id: str,
    character_id: str,
    image: Image,
    name: str,
    voice_id: str,
) -> None:
    """
    Set book character
    """
    call_no_return(
        "botCodeFileBookCharacterSet",
        {
            "file_id": file_id,
            "character_id": character_id,
            "image": image,
            "name": name,
            "voice_id": voice_id,
        },
    )


def file_book_page_add(
    file_id: str,
    image: Optional[Image] = None,
) -> int:
    """
    Create book page
    """
    result: Dict[Any, Any] = call_return(
        "botCodeFileBookPageSet",
        {
            "file_id": file_id,
            "image": image,
        },
    )

    return result.get("page_index", 0)


def file_book_page_line_add(
    file_id: str,
    page_index: int,
    character_id: str,
    markdown: str,
) -> int:
    """
    Create book page line
    """
    result: Dict[Any, Any] = call_return(
        "botCodeFileBookPageLineSet",
        {
            "file_id": file_id,
            "page_index": page_index,
            "line": {
                "character_id": character_id,
                "markdown": markdown,
            },
        },
    )

    return result.get("line_index", 0)


def file_book_user_context_set(
    file_id: str,
    page_index: Optional[int] = None,
    line_index: Optional[int] = None,
) -> int:
    """
    Create book page line
    """
    return call_return(
        "botCodeFileBookUserContextSet",
        {
            "file_id": file_id,
            "fields": {
                "page_index": page_index,
                "line_index": line_index,
            },
        },
    ).line_index


def file_to_text_gen_message(
    file: File,
    role: Optional[TextGenRole] = None,
    include_name: Optional[bool] = None,
    text: Optional[str] = None,
) -> TextGenMessage:
    """
    Convert a file to TextGenMessage, this is useful if you need to pass file into text_gen
    """
    return TextGenMessage(
        **call_return(
            "botCodeFileToTextGenMessage",
            {
                "file": file,
                "role": role,
                "include_name": include_name,
                "text": text,
            },
        )
    )


def markdown_create_image(file_id: str, image: Image) -> str:
    """
    Convert an image into markdown syntax, this will upload the file if it is base64
    """
    return call_return(
        "botCodeMarkdownCreateImage",
        {
            "file_id": file_id,
            "image": image,
        },
    )


def data_set(**kwargs) -> SimpleNamespace:
    """
    Set bot data
    """
    return SimpleNamespace(
        **call_return(
            "botCodeDataSet",
            kwargs,
        )
    )


def data_get() -> SimpleNamespace:
    """
    Get bot data
    """
    return SimpleNamespace(
        **call_return(
            "botCodeDataGet",
            {},
        )
    )


def web_page_get(session_id: str) -> WebPageData:
    """
    Get active web page, this only works when Sociable is being used a sidePanel in Chrome
    """
    result = call_return(
        "botCodeWebPageGet",
        {"session_id": session_id},
    )

    return WebPageData(**result)


def log(
    *args: Any,
) -> None:
    """
    Log, this works the same as print
    """
    call_no_return(
        "botCodeLog",
        {
            "type": "log",
            "args": args,
        },
        case_change=False,
    )


def error(
    *args: Any,
) -> None:
    """
    Log an error
    """
    call_no_return(
        "botCodeLog",
        {
            "type": "error",
            "args": args,
        },
        case_change=False,
    )


def kagi_summarize(url: Optional[str] = None, text: Optional[str] = None):
    """
    Kagi Summarize
    """
    return call_return("kagiSummarize", {"url": url, "text": text})


def kagi_enrich_web(query: str):
    """
    Kagi Enrich Web
    """
    return KagiSearchOutput(**call_return("kagiEnrichWeb", {"query": query}))


def kagi_enrich_news(query: str):
    """
    Kagi Enrich News
    """
    return KagiSearchOutput(
        **call_return(
            "kagiEnrichNews",
            {
                "query": query,
            },
        )
    )


def kagi_search(query: str, limit: Optional[int] = None):
    """
    Kagi Search
    """
    return KagiSearchOutput(
        **call_return("kagiSearch", {"query": query, "limit": limit})
    )
