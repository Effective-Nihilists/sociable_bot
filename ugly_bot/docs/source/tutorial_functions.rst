Text Gen Functions
==========================

`Example <https://ugly.bot/botEdit?botId=d0_2ddm83zciWOQn8hc1M>`_

Many of the LLM models support function calling.

.. admonition:: main.py

    .. code-block:: python
        :name: code
        
        from ugly_bot import *

        @export("user_location_get")
        def func():
            return "Seattle, WA"

        @export("message_direct")
        def text_gen_example(message):
            tool = TextGenTool(
                name="user_location_get",
                description="Get the location of the user",
            )

            history = message_history(limit=50)
            text = text_gen(
                model=TextGenModel.OPENAI_GPT_4O,
                instruction='You are funny and always making jokes.',
                messages=history,
                tools=[tool]
            )
            message_send(markdown=text)

        start()

.. note::
    In the TextGenTool it specifies the name of function to call in the name parameter. Make sure your bot exports a function with a matching name. If you need parameters for your function specify the parameters field using JSON schema. Ugly will map those parameters to your named arguments.


**Glossary**

* `TextGenModel <api.html#ugly_bot.TextGenModel>`_
* `text_gen <api.html#ugly_bot.text_gen>`_
* `message_send <api.html#ugly_bot.message_send>`_
* `message_history <api.html#ugly_bot.message_history>`_
* `TextGenTool <api.html#ugly_bot.TextGenTool>`_