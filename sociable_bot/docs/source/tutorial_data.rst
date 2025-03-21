.. _tutorial_data:

Bot Data
==========================

`Example <https://sociable.bot/botEdit?botId=ILsEsCbxkg4-cRvUlPHue>`_

:ref:`concept_bot_lifetime` is not infinite, so you need someplace to store your data.

.. note::
    Data is stored per conversation. In **data_set** it will only update the fields that you pass in.

.. admonition:: main.py

    .. code-block:: python
        :name: code
        
        from sociable_bot import *

        @export("message_direct")
        def example():
            data = data_get()
            data = data_set(
                counter = data.counter + 1 if hasattr(data, "counter") else 0
            )

            message_send(text = data.counter)

        start()

.. note::
    Since data is stored per conversation and the **conversation_start** event is always triggered at the start of a conversation, you can use that event to initialize your data.

.. admonition:: main.py

    .. code-block:: python
        :name: code2
        
        from sociable_bot import *

        @export("conversation_start")
        def init():
            data = data_set(
                counter = 100,
                other_value = "Hello"
            )
            
        @export("message_direct")
        def example():
            data = data_get()
            data = data_set(
                counter = data.counter + 1
            )

            message_send(text = f"{data.other_value} {data.counter}")

        start()

**Glossary**

* `data_get <api.rst#sociable_bot.data_get>`_
* `data_set <api.rst#sociable_bot.data_set>`_
* `message_send <api.rst#sociable_bot.message_send>`_