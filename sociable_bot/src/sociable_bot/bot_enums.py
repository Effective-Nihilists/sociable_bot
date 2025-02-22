from enum import StrEnum


class UserLang(StrEnum):
    AR = "ar"
    DE = "de"
    EN = "en"
    ES = "es"
    FA = "fa"
    FR = "fr"
    HI = "hi"
    IT = "it"
    JA = "ja"
    PT = "pt"
    RU = "ru"
    TL = "tl"
    TR = "tr"
    VI = "vi"
    ZH = "zh"


class ImageGenModel(StrEnum):
    FAL_SDXL = "fal_sdxl"
    FAL_SDXL_LIGHTNING = "fal_sdxl_lightning"
    FAL_SD3 = "fal_sd3"
    FAL_FLUX_SCHNELL = "fal_flux_schnell"
    FAL_FLUX_DEV = "fal_flux_dev"
    FAL_FLUX_PRO = "fal_flux_pro"


class ImageGenSize(StrEnum):
    SQUARE_HD = "square_hd"
    SQUARE = "square"
    PORTRAIT_4_3 = "portrait_4_3"
    PORTRAIT_16_9 = "portrait_16_9"
    LANDSCAPE_4_3 = "landscape_4_3"
    LANDSCAPE_16_9 = "landscape_16_9"


class MessageVisibility(StrEnum):
    NORMAL = "normal"
    SILENT = "silent"
    HIDDEN = "hidden"


class MessageColor(StrEnum):
    ACCENT = "accent"
    ERROR = "error"


class Mood(StrEnum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    ANGRY = "angry"
    SAD = "sad"
    FEAR = "fear"
    DISGUST = "disgust"
    LOVE = "love"
    SLEEP = "sleep"


class ButtonType(StrEnum):
    PRIMARY = "primary"
    DEFAULT = "default"
    ERROR = "error"
    DEBUG = "debug"


class MessageIcon(StrEnum):
    WEB = "web"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    X = "x"
    THREADS = "threads"
    FACEBOOK = "facebook"
    PINTEREST = "pinterest"
    WHATSAPP = "whatsapp"
    SNAPCHAT = "snapchat"


class FileType(StrEnum):
    MARKDOWN = "markdown"
    LINK = "link"
    IMAGE = "image"
    PDF = "pdf"
    BOT = "bot"
    AUDIO = "audio"
    VIDEO = "video"


class BotTag(StrEnum):
    CHAT = "chat"
    MODERATOR = "moderator"
    TRANSLATOR = "translator"
    TOOL = "tool"
    FEED = "feed"
    DOC = "doc"
    VIDEO = "video"
    CRON = "cron"


class Timezone(StrEnum):
    PACIFIC_MIDWAY = "Pacific/Midway"
    PACIFIC_HONOLULU = "Pacific/Honolulu"
    AMERICA_JUNEAU = "America/Juneau"
    AMERICA_BOISE = "America/Boise"
    AMERICA_DAWSON = "America/Dawson"
    AMERICA_CHIHUAHUA = "America/Chihuahua"
    AMERICA_PHOENIX = "America/Phoenix"
    AMERICA_CHICAGO = "America/Chicago"
    AMERICA_REGINA = "America/Regina"
    AMERICA_MEXICO_CITY = "America/Mexico_City"
    AMERICA_BELIZE = "America/Belize"
    AMERICA_DETROIT = "America/Detroit"
    AMERICA_BOGOTA = "America/Bogota"
    AMERICA_CARACAS = "America/Caracas"
    AMERICA_SANTIAGO = "America/Santiago"
    AMERICA_ST_JOHNS = "America/St_Johns"
    AMERICA_SAO_PAULO = "America/Sao_Paulo"
    AMERICA_TIJUANA = "America/Tijuana"
    AMERICA_MONTEVIDEO = "America/Montevideo"
    AMERICA_ARGENTINA_BUENOS_AIRES = "America/Argentina/Buenos_Aires"
    AMERICA_GODTHAB = "America/Godthab"
    AMERICA_LOS_ANGELES = "America/Los_Angeles"
    ATLANTIC_AZORES = "Atlantic/Azores"
    ATLANTIC_CAPE_VERDE = "Atlantic/Cape_Verde"
    UTC = "UTC"
    EUROPE_LONDON = "Europe/London"
    EUROPE_DUBLIN = "Europe/Dublin"
    EUROPE_LISBON = "Europe/Lisbon"
    AFRICA_CASABLANCA = "Africa/Casablanca"
    ATLANTIC_CANARY = "Atlantic/Canary"
    EUROPE_BELGRADE = "Europe/Belgrade"
    EUROPE_SARAJEVO = "Europe/Sarajevo"
    EUROPE_BRUSSELS = "Europe/Brussels"
    EUROPE_AMSTERDAM = "Europe/Amsterdam"
    AFRICA_ALGIERS = "Africa/Algiers"
    EUROPE_BUCHAREST = "Europe/Bucharest"
    AFRICA_CAIRO = "Africa/Cairo"
    EUROPE_HELSINKI = "Europe/Helsinki"
    EUROPE_ATHENS = "Europe/Athens"
    ASIA_JERUSALEM = "Asia/Jerusalem"
    AFRICA_HARARE = "Africa/Harare"
    EUROPE_MOSCOW = "Europe/Moscow"
    ASIA_KUWAIT = "Asia/Kuwait"
    AFRICA_NAIROBI = "Africa/Nairobi"
    ASIA_BAGHDAD = "Asia/Baghdad"
    ASIA_TEHRAN = "Asia/Tehran"
    ASIA_DUBAI = "Asia/Dubai"
    ASIA_BAKU = "Asia/Baku"
    ASIA_KABUL = "Asia/Kabul"
    ASIA_YEKATERINBURG = "Asia/Yekaterinburg"
    ASIA_KARACHI = "Asia/Karachi"
    ASIA_KOLKATA = "Asia/Kolkata"
    ASIA_KATHMANDU = "Asia/Kathmandu"
    ASIA_DHAKA = "Asia/Dhaka"
    ASIA_COLOMBO = "Asia/Colombo"
    ASIA_ALMATY = "Asia/Almaty"
    ASIA_RANGOON = "Asia/Rangoon"
    ASIA_BANGKOK = "Asia/Bangkok"
    ASIA_KRASNOYARSK = "Asia/Krasnoyarsk"
    ASIA_SHANGHAI = "Asia/Shanghai"
    ASIA_KUALA_LUMPUR = "Asia/Kuala_Lumpur"
    ASIA_TAIPEI = "Asia/Taipei"
    AUSTRALIA_PERTH = "Australia/Perth"
    ASIA_IRKUTSK = "Asia/Irkutsk"
    ASIA_SEOUL = "Asia/Seoul"
    ASIA_TOKYO = "Asia/Tokyo"
    ASIA_YAKUTSK = "Asia/Yakutsk"
    AUSTRALIA_DARWIN = "Australia/Darwin"
    AUSTRALIA_ADELAIDE = "Australia/Adelaide"
    AUSTRALIA_SYDNEY = "Australia/Sydney"
    AUSTRALIA_BRISBANE = "Australia/Brisbane"
    AUSTRALIA_HOBART = "Australia/Hobart"
    ASIA_VLADIVOSTOK = "Asia/Vladivostok"
    PACIFIC_GUAM = "Pacific/Guam"
    ASIA_MAGADAN = "Asia/Magadan"
    ASIA_KAMCHATKA = "Asia/Kamchatka"
    PACIFIC_FIJI = "Pacific/Fiji"
    PACIFIC_AUCKLAND = "Pacific/Auckland"
    PACIFIC_TONGATAPU = "Pacific/Tongatapu"


class ConversationType(StrEnum):
    HUMAN = "human"
    GROUP = "group"
    BOT = "bot"
    FILE = "file"


class TextGenRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class TextGenModel(StrEnum):
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
    ANTHROPHIC_CLAUDE_3_OPUS = "anthrophic_claude_3_opus"
    ANTHROPHIC_CLAUDE_3_SONNET = "anthrophic_claude_3_sonnet"
    ANTHROPHIC_CLAUDE_3_HAIKU = "anthrophic_claude_3_haiku"
    PERPLEXITY_LLAMA_3_SONAR_SMALL_128K_ONLINE = (
        "perplexity_llama_3_sonar_small_128k_online"
    )
    PERPLEXITY_LLAMA_3_SONAR_LARGE_128K_ONLINE = (
        "perplexity_llama_3_sonar_large_128k_online"
    )
    PERPLEXITY_LLAMA_3_SONAR_HUGE_128K_ONLINE = (
        "perplexity_llama_3_sonar_huge_128k_online"
    )
    OPENAI_GPT_4 = "openai_gpt_4"
    OPENAI_GPT_4_32K = "openai_gpt_4_32k"
    OPENAI_GPT_4_TURBO = "openai_gpt_4_turbo"
    OPENAI_GPT_4O = "openai_gpt_4o"
    OPENAI_GPT_3_TURBO = "openai_gpt_3_turbo"
    OPENAI_GPT_3_TURBO_16K = "openai_gpt_3_turbo_16k"
    OPENAI_O1 = "openai_o1"
    OPENAI_O1_MINI = "openai_o1_mini"
