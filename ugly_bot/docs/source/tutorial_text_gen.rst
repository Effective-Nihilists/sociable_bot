Text Gen (LLM)
==========================

`Example <https://ugly.bot/botEdit?botId=dO-0ZeajunivGXqAYUzGc>`_

Let's build a really dumb chat bot that responds to the last message sent using text_gen (LLM).

.. warning::
    Make sure you understand how to create a bot from :ref:`tutorial_hello` tutorial

.. admonition:: main.py

    .. code-block:: python
        :name: code
        
        from ugly_bot import *

        @export("message_direct")
        def text_gen_example(message):
            text = text_gen(
                model=TextGenModel.TOGETHER_META_LLAMA_3_8B,
                question=f"Explain {message.text} to me"
            )
            message_send(text=text)

        start()

.. note::
    When a user writes a message, Ugly will check if the bot has exported a "message_direct" function. If so, it will pass the message into that function. The bot will then send the text of the message to text_gen to run AI. The AI will return a string which is then sent back into the conversation.

**Glossary**

* `TextGenModel <api.html#ugly_bot.TextGenModel>`_
* `text_gen <api.html#ugly_bot.text_gen>`_
* `message_send <api.html#ugly_bot.message_send>`_