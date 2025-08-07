Buttons
==========================

`Example <https://ugly.bot/botEdit?botId=ID1qpW_Dl9nVpcbbkVN5L>`_

Add some basic interactivity

.. warning::
    :ref:`conversation_start <concept_export>` runs the first time a conversation is create or after you **wipe** the conversation using the "..." menu


.. admonition:: main.py

    .. code-block:: python
        :name: code
        
        from ugly_bot import *

        @export("run_this")
        def run_this():
            message_send(text="I ran this")
            
        @export("conversation_start")
        def fun():
            conversation_buttons_show(
                buttons=[
                    Button(
                        type=ButtonType.BUTTON,
                        text="Normal Button",
                        func="run_this"
                    ),
                    Button(
                        type=ButtonType.LINK,
                        text="Link Button",
                        uri="https://ugly.bot"
                    ),
                    Button(
                        type=ButtonType.TEXT,
                        text="Text Button"
                    )
                ]
            )

        start()

**Glossary**

* `conversation_buttons_show <api.html#ugly_bot.conversation_buttons_show>`_
* `Button <api.html#ugly_bot.Button>`_
* `ButtonType <api.html#ugly_bot.ButtonType>`_
