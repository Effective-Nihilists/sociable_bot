from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, Protocol, Union


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


class FileType:
    pass


class BotTag:
    pass


class Avatar:
    pass


class Timezone:
    pass


class Emotion:
    pass


class ConversationType:
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


class ImageType(Enum):
    PUBLIC = "public"
    URI = "uri"
    BASE64 = "base64"


class CodeTextGenRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"


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


class CodeUser:
    def __init__(
        self,
        userId: str,
        name: str,
        bio: str,
        avatar: Avatar,
        voiceId: Optional[str],
        birthday: Optional[int],
        type: str,
        lang: UserLangT,
        timezone: Timezone,
        calendly: Optional[str] = None,
    ):
        self.userId = userId
        self.name = name
        self.bio = bio
        self.avatar = avatar
        self.voiceId = voiceId
        self.birthday = birthday
        self.type = type
        self.lang = lang
        self.calendly = calendly
        self.timezone = timezone


class CodeUserPrivate:
    def __init__(self, userId: str, calendly: Optional[str], email: Optional[str]):
        self.userId = userId
        self.calendly = calendly
        self.email = email


class CodeLiveUser:
    def __init__(
        self,
        userId: str,
        emotion: Optional[Emotion],
        image: Optional[ImageBase64Result],
    ):
        self.userId = userId
        self.emotion = emotion
        self.image = image


class CodeBot:
    def __init__(self, userId: str, name: str, bio: str, tags: List[BotTag]):
        self.userId = userId
        self.name = name
        self.bio = bio
        self.tags = tags


class CodeFileCommon:
    def __init__(
        self,
        id: str,
        userId: str,
        type: FileType,
        title: str,
        text: Optional[str],
        **kwargs: Any
    ):
        self.id = id
        self.userId = userId
        self.type = type
        self.title = title
        self.text = text
        for key, value in kwargs.items():
            setattr(self, key, value)


class CodeFileMarkdown(CodeFileCommon):
    def __init__(
        self,
        id: str,
        userId: str,
        title: str,
        markdown: str,
        text: Optional[str] = None,
    ):
        super().__init__(id, userId, "markdown", title, text)
        self.markdown = markdown


class CodeFileImage(CodeFileCommon):
    def __init__(
        self,
        id: str,
        userId: str,
        title: str,
        image: ImagePublic,
        thumbnail: ImagePublic,
        text: Optional[str] = None,
    ):
        super().__init__(id, userId, "image", title, text)
        self.image = image
        self.thumbnail = thumbnail


class CodeFilePdf(CodeFileCommon):
    def __init__(
        self, id: str, userId: str, title: str, uri: str, text: Optional[str] = None
    ):
        super().__init__(id, userId, "pdf", title, text)
        self.uri = uri


class CodeFileLink(CodeFileCommon):
    def __init__(
        self, id: str, userId: str, title: str, uri: str, text: Optional[str] = None
    ):
        super().__init__(id, userId, "link", title, text)
        self.uri = uri


class CodeFileBot(CodeFileCommon):
    def __init__(self, id: str, userId: str, title: str, text: Optional[str] = None):
        super().__init__(id, userId, "bot", title, text)


CodeFile = Union[
    CodeFileMarkdown, CodeFileBot, CodeFileImage, CodeFilePdf, CodeFileLink
]


class CodeMeeting:
    def __init__(self, id: str, timezone: Timezone):
        self.id = id
        self.timezone = timezone


class CodeConversation:
    def __init__(
        self, id: str, type: ConversationType, title: str, fileId: Optional[str] = None
    ):
        self.id = id
        self.type = type
        self.title = title
        self.fileId = fileId


class MessageDirectProtocol(Protocol):
    async def __call__(self, message: CodeMessage) -> None: ...


class MessageAddProtocol(Protocol):
    async def __call__(self, message: CodeMessage) -> None: ...


class BotHourlyProtocol(Protocol):
    async def __call__(self, hour: int) -> None: ...


class FileCreateProtocol(Protocol):
    async def __call__(self, file: CodeFile) -> None: ...


class ConversationHourlyProtocol(Protocol):
    async def __call__(self, hour: int) -> None: ...


class ConversationStartProtocol(Protocol):
    async def __call__(self, conversation: CodeConversation) -> None: ...


class ConversationUserAddProtocol(Protocol):
    async def __call__(
        self, user: CodeUser, conversation: CodeConversation
    ) -> None: ...


class MeetingStartProtocol(Protocol):
    async def __call__(
        self, conversation: CodeConversation, meeting: CodeMeeting
    ) -> None: ...


class MeetingStopProtocol(Protocol):
    async def __call__(
        self, conversation: CodeConversation, meeting: CodeMeeting
    ) -> None: ...


class MeetingUserVisibleProtocol(Protocol):
    async def __call__(
        self, conversation: CodeConversation, meeting: CodeMeeting, user: CodeUser
    ) -> None: ...


class ThreadStopProtocol(Protocol):
    async def __call__(self, thread: Thread) -> None: ...


class InputChangedProtocol(Protocol):
    async def __call__(self, user_id: str, text: str) -> None: ...
