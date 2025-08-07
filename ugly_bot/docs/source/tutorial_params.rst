Bot Params
==========================

`Example <https://ugly.bot/botEdit?botId=A8vnD6HE-g2Lgqe8P5YX3>`_

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
        
        from ugly_bot import *

        @export("message_direct")
        def example():
            message_send(text=getattr(bot_params, "name", "Not Set"))


        start()


**Glossary**

* `message_send <api.html#ugly_bot.message_send>`_
* `JSON Schema <https://json-schema.org/learn/miscellaneous-examples>`_