from enum import StrEnum
import inspect
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from .bot_enums import *

funcs = {}

name_map = {
    "message_direct": "messageDirect",
    "message_add": "messageAdd",
    "bot_hourly": "botHourly",
    "file_create": "fileCreate",
    "conversation_hourly": "conversationHourly",
    "conversation_start": "conversationStart",
    "conversation_user_add": "conversationUserAdd",
    "meeting_start": "meetingStart",
    "meeting_stop": "meetingStop",
    "meeting_user_visible": "meetingUserVisible",
    "thread_stop": "threadStop",
    "input_changed": "inputChanged",
}


def export(name: str):
    def inner(func):
        global funcs

        sig = inspect.signature(func)
        parameters = sig.parameters.values()

        # Check if function accepts arbitrary kwargs (**kwargs)
        accepts_kwargs = any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in parameters
        )

        # Collect allowed parameter names if no **kwargs
        allowed_params = set()
        if not accepts_kwargs:
            for param in parameters:
                if param.kind in (
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    inspect.Parameter.KEYWORD_ONLY,
                ):
                    allowed_params.add(param.name)

        def wrapper(**kwargs):
            if not accepts_kwargs:
                # Filter kwargs to only allowed parameters
                filtered_kwargs = {
                    k: v for k, v in kwargs.items() if k in allowed_params
                }
                return func(**filtered_kwargs)
            return func(**kwargs)

        mapped_name = name_map.get(name)

        funcs[mapped_name if mapped_name is not None else name] = wrapper

        return func

    return inner


class ImageType(StrEnum):
    PUBLIC = "public"
    URI = "uri"
    BASE64 = "base64"


@dataclass
class ImagePublic:
    uri: str
    width: int
    height: int
    prompt: Optional[str] = None
    type: ImageType = ImageType.PUBLIC


@dataclass
class ImageUriResult:
    uri: Optional[str]
    width: int
    height: int
    prompt: Optional[str] = None
    type: ImageType = ImageType.URI


@dataclass
class ImageBase64Result:
    base64: str
    width: int
    height: int
    prompt: Optional[str] = None
    type: ImageType = ImageType.BASE64


ImageResult = Union[ImageBase64Result, ImageUriResult, ImagePublic]


@dataclass
class Thread:
    id: str
    type: str
    meetingId: Optional[str] = None
    messageId: Optional[str] = None
    sectionId: Optional[str] = None


@dataclass
class MessageButtonBase:
    type: str


@dataclass
class MessageButtonLink(MessageButtonBase):
    icon: MessageIcon
    text: str
    uri: str

    def __post_init__(self):
        self.type = "link"


@dataclass
class MessageButtonText(MessageButtonBase):
    text: str
    lang: Optional[UserLang] = None

    def __post_init__(self):
        self.type = "text"


@dataclass
class MessageButtonNormal(MessageButtonBase):
    text: str
    func: str
    params: Optional[Dict[str, Any]] = None
    buttonType: Optional[ButtonType] = None

    def __post_init__(self):
        self.type = "button"


MessageButton = Union[MessageButtonNormal, MessageButtonText, MessageButtonLink]


@dataclass
class Message:
    id: str
    created: int
    userId: str
    text: str
    isBot: bool
    markdown: Optional[str] = None
    system: Optional[bool] = None
    mentionUserIds: Optional[List[str]] = None
    lang: Optional[UserLang] = None
    onlyUserIds: Optional[List[str]] = None
    visibility: Optional[MessageVisibility] = None
    color: Optional[MessageColor] = None
    buttons: Optional[List[MessageButton]] = None
    mood: Optional[Mood] = None
    impersonateUserId: Optional[str] = None
    fileIds: Optional[List[str]] = None
    contextFileId: Optional[str] = None
    thread: Optional[Thread] = None


TextGenMessageContent = Union[str, ImageUriResult, ImageBase64Result]


@dataclass
class TextGenMessage:
    role: TextGenRole
    content: Union[str, List[TextGenMessageContent]]


@dataclass
class TextGenTool:
    name: str
    description: str
    parameters: Optional[Dict[str, Any]] = None


@dataclass
class Avatar:
    image: ImageResult
    background: Optional[ImageResult]


@dataclass
class User:
    id: str
    name: str
    bio: str
    avatar: Avatar
    voiceId: Optional[str]
    birthday: Optional[int]
    type: str
    lang: UserLang
    timezone: Timezone
    calendly: Optional[str] = None


@dataclass
class UserPrivate:
    id: str
    calendly: Optional[str]
    email: Optional[str]


@dataclass
class Emotion:
    neutral: int
    happy: int
    sad: int
    angry: int
    fearful: int
    disgusted: int
    surprised: int


@dataclass
class LiveUser:
    id: str
    emotion: Optional[Emotion]
    image: Optional[ImageBase64Result]


@dataclass
class Bot:
    id: str
    name: str
    bio: str
    tags: List[BotTag]


@dataclass
class File:
    id: str
    userId: str
    type: FileType
    title: str
    text: Optional[str]
    image: ImagePublic
    thumbnail: ImagePublic
    markdown: str
    uri: str


@dataclass
class Meeting:
    id: str
    timezone: "Timezone"


@dataclass
class Conversation:
    id: str
    type: "ConversationType"
    title: str
    fileId: Optional[str] = None


@dataclass
class NewsArticle:
    title: str
    content: str
    uri: Optional[str]


@dataclass
class FileChunk:
    fileId: str
    text: str


@dataclass
class SearchArticle:
    title: str
    synopsis: str
    uri: Optional[str]


class ConversationContentType(StrEnum):
    FILE = "file"
    URI = "uri"


@dataclass
class ConversationFileContent:
    fileId: str
    disabled: bool
    type: ConversationContentType = ConversationContentType.FILE


@dataclass
class ConversationUriContent:
    uri: str
    type: ConversationContentType = ConversationContentType.URI


ConversationContent = Union[ConversationFileContent, ConversationUriContent]


class FileSectionType(StrEnum):
    MARKDOWN = "markdown"


@dataclass
class FileSectionCommon:
    id: str
    type: FileSectionType
    title: Optional[str] = None
    thread: Optional[bool] = None


@dataclass
class FileSectionMarkdown(FileSectionCommon):
    markdown: Optional[str] = None
    placeholder: Optional[str] = None
    editable: Optional[bool] = None
    type: FileSectionType = FileSectionType.MARKDOWN


FileSection = Union[FileSectionMarkdown]


@dataclass
class Event:
    id: str
    start: int
    end: int
