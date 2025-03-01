Tool
==========================

Tools are bots that can be used in any conversation.

.. warning::
    Make sure to add the :ref:`tool tag <concept_export>` to the bot. After you add the tag, click on "Add Tool". Open any conversation and click on the "Tool icon" (it looks like a hammer in a circle) to show the tool bots and select your bot.

.. admonition:: main.py

    .. code-block:: python
        :name: code
        
        from sociable_bot import *

        @export("message_direct")
        def example():            
            message_send(text="This came from your tool")

        start()

.. note::
    Tools have the unique ability to respond as the user it typing using the :ref:`input_changed event <concept_export>`.

.. admonition:: main.py

    .. code-block:: python
        :name: code2
        
        from sociable_bot import *

        @export("send_message")
        def send(msg):
            message_send(text=msg)

        @export("input_changed")
        def example(user_id, text): 
            msg = f"{text} lah"           
            conversation_buttons_show(
                buttons=[
                    Button(
                        type=ButtonType.BUTTON,
                        text=msg,
                        func="send_message",
                        params={
                            "msg": msg
                        }
                    ),
                ]
            )

        start()

**Glossary**

* `message_send <api.html#sociable_bot.message_send>`_
* `conversation_buttons_show <api.html#sociable_bot.conversation_buttons_show>`_