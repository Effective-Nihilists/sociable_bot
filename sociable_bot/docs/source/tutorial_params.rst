Bot Params
==========================

Make your bot customizable

.. warning::
    In the settings tab for the bot, set the name field to something

.. admonition:: params.json

    .. code-block:: json
        :name: params
        
        { 
            "type": "object",
            "properties": {
                "name": { 
                    "type": "string"
                }
            }
        }


.. admonition:: main.py

    .. code-block:: python
        :name: code
        
        from sociable_bot import *

        @export("message_direct")
        def example():
            message_send(text=bot_params["name"])


        start()


**Glossary**

* `message_send <api.html#sociable_bot.message_send>`_
* `JSON Schema <https://json-schema.org/learn/miscellaneous-examples>`_