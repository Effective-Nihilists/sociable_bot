
Export / Tags
==========================

A Bot exports functions, so Sociable can trigger different actions. There are some built-in actions that can be registered. Some of them require a specific bot tag to enable them, refer to below. Bots can also export custom actions which can be used by text_gen function calling or buttons. Exports use the "export" decorator to identify which functions are exported, the name of the function does not matter and multiple decorators can be used on the same function

.. admonition:: main.py

    .. code-block:: python
        :name: code
        
        from sociable_bot import *

        @export("message_direct")
        def message_direct(message: Message, conversation: Conversation):
            # This is called when a user sends a message:
            # * in a 1:1 conversation with this bot, requires tag "chat"
            # * mentions this bot in a message, requires tag "chat" or "tool"
        
        @export("message_add")
        def message_add(message: Message, conversation: Conversation):
            # This is called when a user sends a message in a group chat
            # requires tag "chat"

        @export("bot_hourly")
        def bot_hourly(hour: int):
            # This call once an hour, hour is the hour of the day in UTC/GMT time
            # Requires tag "cron"

        @export("conversation_hourly")
        def bot_hourly(hour: int):
            # This call once an hour for every conversation where this bot is
            # a member, hour is the hour of the day in UTC/GMT time
            # Requires tag "cron"

        @export("conversation_start")
        def conversation_start(conversation: Conversatiot):
            # This call once an hour for every conversation where this bot is 
            # a member, hour is the hour of the day in UTC/GMT time
            # Requires tag "cron"
            
        @export("conversation_user_add")
        def conversation_user_add(user: User, conversation: Conversation):
            # This is called when a user is added to a conversation
            # requires tag "chat"

        @export("video_call_start")
        def video_call_start(video_call: VideoCall, conversation: Conversation):
            # This is called when a video call starts
            # requires tag "video"

        @export("video_call_stop")
        def video_call_stop(video_call: VideoCall, conversation: Conversation):
            # This is called when a video call ends
            # requires tag "video"

        @export("video_call_user_visible")
        def video_call_user_visible(
            live: LiveUser, 
            video_call: VideoCall, 
            conversation: Conversation
        ):
            # This is called when a user's video is available for the first time
            # requires tag "video"

        @export("thread_stop")
        def thread_stop(thread: Thread):
            # This is called when a thread ends, all meetings are threads also 
            # user's can manually create new threads
            # requires tag "chat"

        @export("input_changed")
        def input_changed(user_id: str, text: str):
            # This is called as the user is typing, only if the bot is selected 
            # in the bot toolbar
            # requires tag "tool"

        @export("web_page_updated")
        def web_page_updated(
            user_id: str, 
            session_id: str, 
            url: string, 
            title: string
        ):
            # This is called when the active web page changes, only works when 
            # Sociable is used a side panel in Chrome
            # requires tag "web"

        
        @export("message_direct")
        @export("message_add")
        def any_message(message: Message, conversation: Conversation):
            # This is valid
