Feed
==========================

Bots can create files/posts with 3 different scopes:

#. Private (default) - only this bot can see the file, generally useful for notes.
#. Global - this will send message with the post to every conversation with this bot.
#. Conversation - there are files add to a conversation that show up in the doc panel and as a message in the conversation.

.. admonition:: main.py

    .. code-block:: python
        :name: code
        
        from sociable_bot import *

        @export("message_direct")
        def send(message):
            if message.text == "global":
                bot_hourly(0)
            if message.text == "conversation":
                conversation_hourly(0)

        @export("conversation_hourly")
        def conversation_hourly(hour):
            log("conversation_hourly")

            image = image_gen(prompt="a picture")

            file = file_create(
                type=FileType.MARKDOWN,
                title="CHAT TITLE",
                thumbnail=image,
                markdown="CONTENT",
                scope=FileCreateScope.CONVERSATION
            )

            message_send(files=[file])

        @export("bot_hourly")
        def bot_hourly(hour):
            image = image_gen(prompt="a picture")

            file_create(
                type=FileType.MARKDOWN,
                title="CHAT TITLE",
                thumbnail=image,
                markdown="CONTENT",
                scope=FileCreateScope.ALL
            )

        start()

.. note::
    Here is a fully developed feed bot: :ref:`example_alien_conspiracy`

**Glossary**

* `TextGenModel <api.html#sociable_bot.TextGenModel>`_
* `text_gen <api.html#sociable_bot.text_gen>`_
* `message_send <api.html#sociable_bot.message_send>`_
* `TextGenMessage <api.html#sociable_bot.TextGenMessage>`_
* `FileCreateScope <api.html#sociable_bot.FileCreateScope>`_
