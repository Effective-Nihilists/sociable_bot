Vision
==========================

Open your bot's eyes

.. warning::
    Make sure you understand how to create a bot from :ref:`tutorial_hello` tutorial

.. admonition:: main.py

    .. code-block:: python
        :name: code
        
        from sociable_bot import *

        @export("video_call_user_visible")
        def example(live_user):
            text = text_gen(
                model=TextGenModel.OPENAI_GPT_4O,
                instruction='You are funny and always making jokes.',
                messages=[
                    TextGenMessage(
                        role = TextGenRole.USER,
                        content = [
                            live_user.image,
                            "Describe this image"
                        ]
                    ),
                ],
            )
            message_send(markdown=text)

        start()

.. note::
    In the TextGenTool it specifies the name of function to call in the name parameter. Make sure your bot exports a function with a matching name. If you need parameters for your function specify the parameters field using JSON schema. Sociable will map those parameters to your named arguments.


**Glossary**

* `TextGenModel <api.html#sociable_bot.TextGenModel>`_
* `text_gen <api.html#sociable_bot.text_gen>`_
* `message_send <api.html#sociable_bot.message_send>`_
* `message_history <api.html#sociable_bot.message_history>`_
* `TextGenTool <api.html#sociable_bot.TextGenTool>`_