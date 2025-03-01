Chat Bot
==========================

Let's build ChatGPT

.. warning::
    Make sure you understand how to create a bot from :ref:`tutorial_hello` tutorial

.. admonition:: main.py

    .. code-block:: python
        :name: code
        
        from sociable_bot import *

        @export("message_direct")
        def text_gen_example(message):
            history = message_history(limit=50)
            text = text_gen(
                model=TextGenModel.TOGETHER_META_LLAMA_3_8B,
                instruction='You are funny and always making jokes.',
                messages=history
            )
            message_send(markdown=text)

        start()

.. note::
    If you compare this with the text_gen tutorial, you can see a few key changes:

    #. message_history is called to get the messages sent in this chat
    #. text_gen is passed instruction & message instead of question
    #. message_send is passed markdown instead text, this lets Sociable render the text using markdown syntax which is a very common output of an LLM. This is great for bold, bullet points, tables, etc.

**Glossary**

* `TextGenModel <api.html#sociable_bot.TextGenModel>`_
* `text_gen <api.html#sociable_bot.text_gen>`_
* `message_send <api.html#sociable_bot.message_send>`_
* `message_history <api.html#sociable_bot.message_history>`_