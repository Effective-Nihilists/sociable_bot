.. _tutorial_data:

Bot Data
==========================

:ref:`concept_bot_lifetime` is not infinite, so you need someplace to store your data.

.. warning::
    Make sure you understand how to create a bot from :ref:`tutorial_hello` tutorial

.. admonition:: main.py

    .. code-block:: python
        :name: code
        
        from sociable_bot import *

        @export("message_direct")
        def text_gen_example(message):
            text = text_gen(
                model=TextGenModel.TOGETHER_META_LLAMA_3_8B,
                question=f"Explain {message.text} to me"
            )
            message_send(text=text)

        start()

**Glossary**

* `TextGenModel <api.rst#sociable_bot.TextGenModel>`_
* `text_gen <api.rst#sociable_bot.text_gen>`_
* `message_send <api.rst#sociable_bot.message_send>`_