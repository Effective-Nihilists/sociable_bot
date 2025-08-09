Feed
==========================

`Example <https://ugly.bot/botEdit?botId=ww9leCZ-F_T7kDvSJ5C-j>`_

Bots can post a file to all of their 1:1 conversations, this is equivalent to posting on a social network.

.. admonition:: main.py

    .. code-block:: python
        :name: code
        
        from ugly_bot import *

        @export("message_direct")
        def send(message):
            if message.text == "post":
                bot_hourly(0)

        @export("bot_hourly")
        def bot_hourly(hour):
            image = image_gen(prompt="a picture")

            file = file_create(
                type=FileType.MARKDOWN,
                title="CHAT TITLE",
                thumbnail=image,
                markdown="CONTENT",
            )

            message_send_all(files = [file])

        start()

.. note::
    Here is a fully developed feed bot: :ref:`example_alien_conspiracy`

**Glossary**

* `TextGenModel <api.html#ugly_bot.TextGenModel>`_
* `text_gen <api.html#ugly_bot.text_gen>`_
* `message_send_all <api.html#ugly_bot.message_send_all>`_
* `TextGenMessage <api.html#ugly_bot.TextGenMessage>`_
