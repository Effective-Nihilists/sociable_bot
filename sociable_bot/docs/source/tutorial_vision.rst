Vision
==========================

Open your bot's eyes

.. admonition:: main.py

    .. code-block:: python
        :name: code
        
        from sociable_bot import *

        @export("user_visible")
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
    Vision requires an image, so we trigger on event :ref:`user_visible <concept_export>` which happens when a user becomes visible. Also, sending the image to the LLM requires a more complex message format.


**Glossary**

* `TextGenModel <api.html#sociable_bot.TextGenModel>`_
* `text_gen <api.html#sociable_bot.text_gen>`_
* `message_send <api.html#sociable_bot.message_send>`_
* `TextGenMessage <api.html#sociable_bot.TextGenMessage>`_
* `LiveUser <api.html#sociable_bot.LiveUser>`_