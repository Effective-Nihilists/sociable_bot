from dataclasses import asdict, is_dataclass
import os
from typing import Any, Callable, Dict, List, Literal, Optional, Union
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
sio = socketio.Client()
token = sys.argv[2] if sys.argv[1] == "bot" else None
json_data = json.loads(sys.argv[3]) if sys.argv[1] == "bot" else None
bot_params = json_data["params"] if json_data is not None else None
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


def meeting_arg_map(dict: Dict[Any, Any]):
    return {
        "video_call": VideoCall(**dict["meeting"]),
        "conversation": Conversation(**dict["conversation"]),
    }


def live_user_visible_arg_map(dict: Dict[Any, Any]):
    return {
        "live_user": LiveUser(**dict["live_user"]),
        "video_call": VideoCall(**dict["meeting"]),
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
    "meetingStart": meeting_arg_map,
    "meetingStop": meeting_arg_map,
    "meetingUserVisible": live_user_visible_arg_map,
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
    """
    Start your bot, this runs the event loop so your bot can receive calls
    """
    old_print("[BOT] start client socket", app_host)
    sio.connect(f"ws://{app_host}/", auth={"token": token}, retry=True)

    log("[BOT] params", bot_params)

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
    old_print("[BOT] client socket send", op, bot_context, params)
    result = sio.call(
        "call",
        {
            "op": op,
            "input": {
                "context": bot_context,
                "params": convert_keys_to_camel_case(params),
            },
        },
    )
    # print("[BOT] client socket send result", result)
    return (
        convert_keys_to_snake_case(result.get("data")) if result is not None else None
    )


def conversation(id: str) -> Optional[Conversation]:
    """
    Get conversation
    """
    result = call(
        "botCodeConversationGet",
        {
            "id": id,
        },
    )
    return Conversation(**result) if result is not None else None


def user(id: str) -> Optional[User]:
    """
    Get user
    """
    result = call(
        "botCodeUserGet",
        {
            "id": id,
        },
    )
    return User(**result) if result is not None else None


def user_private(id: str) -> Optional[UserPrivate]:
    """
    Get user private
    """
    result = call(
        "botCodeUserPrivateGet",
        {
            "id": id,
        },
    )
    return UserPrivate(**result) if result is not None else None


def live_user(id: str) -> Optional[LiveUser]:
    """
    Get live user
    """
    result = call(
        "botCodeLiveUserGet",
        {
            "id": id,
        },
    )
    return LiveUser(**result) if result is not None else None


def bot(id: str) -> Optional[Bot]:
    """
    Get bot
    """
    result = call(
        "botCodeBotGet",
        {
            "id": id,
        },
    )
    return Bot(**result) if result is not None else None


def bot_owners(id: str) -> List[str]:
    """
    Get owners of a bot
    """
    return call(
        "botCodeBotOwnersGet",
        {"id": id},
    )


def message_typing() -> None:
    """
    Show a typing indicator in the active conversation
    """
    call(
        "botCodeMessageTyping",
        {},
    )


def message_send(
    id: Optional[str] = None,
    text: Optional[str] = None,
    image: Optional[ImageResult] = None,
    images: Optional[List[ImageResult]] = None,
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
        **call(
            "botCodeMessageSend",
            {
                "id": id,
                "text": text,
                "markdown": markdown,
                "image": asdict(image) if image is not None else None,
                "images": (
                    list(map(lambda x: asdict(x), images))
                    if images is not None
                    else None
                ),
                "mentionUserIds": mention_user_ids,
                "onlyUserIds": only_user_ids,
                "lang": lang,
                "visibility": visibility,
                "color": color,
                "buttons": (
                    list(map(lambda x: asdict(x), buttons))
                    if buttons is not None
                    else None
                ),
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
    """
    Edit an existing message
    """
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
    """
    Convert a list of messages into string, useful if you need to add your conversation history to an LLM prompt
    """
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
    """
    Get messages from the active conversation
    """
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
    """
    Generate text using the specified model (LLM)
    """
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
    """
    Get files based on semantic search using the query
    """
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
    """
    Get news based on semantic search using the query
    """
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
) -> Optional[ImageResult]:
    """
    Generate an image using specified model
    """
    result = call(
        "botCodeImageGen",
        {
            "prompt": prompt,
            "model": model,
            "negativePrompt": negative_prompt,
            "size": size,
            "guidanceScale": guidance_scale,
            "steps": steps,
            "image": asdict(image) if image is not None else None,
            "imageStrength": image_strength,
        },
    )
    return ImageResult(**result) if result is not None else None


def google_search(query: str) -> List[SearchArticle]:
    """
    Google search
    """
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
    """
    Send email
    """
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
    """
    Get users for the active conversation
    """
    result = call(
        "botCodeConversationUsers",
        {"type": type, "role": role},
    )

    return list(map(lambda m: User(**m), result))


def conversation_bots(tag: Optional[BotTag] = None) -> List[Bot]:
    """
    Get bots for the active conversation
    """
    result = call(
        "botCodeConversationBots",
        {
            "tag": tag,
        },
    )

    return list(map(lambda m: Bot(**m), result))


def conversation_content_show(content: ConversationContent) -> None:
    """
    Show content in the active conversation
    """
    call(
        "botCodeConversationShowContent",
        asdict(content),
    )


def conversation_buttons_show(
    user_id: Optional[str] = None, buttons: Optional[List[Button]] = None
) -> None:
    """
    Show buttons in the active conversation
    """
    call(
        "botCodeConversationShowButtons",
        {
            "userId": user_id,
            "buttons": (
                list(map(lambda x: asdict(x), buttons)) if buttons is not None else None
            ),
        },
    )


def file_create(
    type: FileType,
    title: str,
    markdown: Optional[str] = None,
    uri: Optional[str] = None,
    thumbnail: Optional[ImageResult] = None,
    lang: Optional[UserLang] = None,
    indexable: Optional[bool] = None,
    message_send: Optional[bool] = None,
    add_to_conversation: Optional[bool] = None,
    add_to_feed: Optional[bool] = None,
    send_notification: Optional[bool] = None,
) -> File:
    """
    Create file
    """
    return File(
        **call(
            "botCodeFileCreate",
            {
                "type": type,
                "title": title,
                "markdown": markdown,
                "uri": uri,
                "thumbnail": asdict(thumbnail) if thumbnail is not None else None,
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
    """
    Update file, only supported on markdown files
    """
    call(
        "botCodeFileUpdate",
        {
            "id": id,
            "title": title,
            "markdown": markdown,
            "thumbnail": asdict(thumbnail) if thumbnail is not None else None,
        },
    )


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


def markdown_create_image(file_id: str, image: ImageResult) -> str:
    """
    Convert an image into markdown syntax, this will upload the file if it is base64
    """
    return call(
        "botCodeMarkdownCreateImage",
        {
            "file_id": file_id,
            "image": asdict(image) if image is not None else None,
        },
    )


def data_set(**kwargs) -> dict:
    """
    Set bot data
    """
    return call(
        "botCodeDataSet",
        kwargs,
    )


def data() -> dict:
    """
    Get bot data
    """
    return call(
        "botCodeDataGet",
        {},
    )


def web_page_get(session_id: str) -> WebPageData:
    """
    Get active web page, this only works when Sociable is being used a sidePanel in Chrome
    """
    result = call(
        "botCodeWebPageGet",
        {"session_id": session_id},
    )

    return WebPageData(**result)


old_print = print


def log(
    *args,
) -> None:
    """
    Log, this works the same as print
    """
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
    *args,
) -> None:
    """
    Log an error
    """
    call(
        "botCodeLog",
        {
            "type": "error",
            "args": list(map(lambda x: asdict(x) if is_dataclass(x) else x, args)),
        },
    )
