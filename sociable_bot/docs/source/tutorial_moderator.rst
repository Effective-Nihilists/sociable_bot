Moderator
==========================

Having a group chat with multiple bots is advanced. It is possible for every bot to individually look at the conversation and decide if it should reply. We found it very difficult to get the right level of engagement from bots using this technique, so we switched to using a silent moderator.

#. Message Receieved
#. Get bot bio & names
#. Send messages and bot data into a magic LLM prompt
#. Use the response to send a silent message to bots to get them to talk

To test this, you will need to create a group chat that includes this bot plus at least one more normal chat bot. You can create a couple chat bot using the built-in Character template. Fill in their bio if you want to make them more interesting to talk with.

.. note::
    The messages used to trigger bots are being sent as SILENT, which means the user can see them but bots cannot not. If you want to hide them from the user change the visibility to HIDDEN.

.. admonition:: main.py

    .. code-block:: python
        :name: code
        
        from sociable_bot import *
        import json


        @export("message_add")
        def send(message):
            message_typing()
            messages = message_history(limit=10)

            # Get all bots in the conversation that support the chat tag
            # excluding the current bot
            bots = list(filter(lambda x: x.id != bot_id, conversation_bots(tag=BotTag.CHAT)))

            # Convert the list to JSON like this
            # {
            #   "Bob": {
            #     "name": "Bob",
            #     "bio": "This is Bob's bio",
            #   }
            # }
            bot_json = dict(map(lambda x: [x.name, {"name": x.name, "bio": x.bio}], bots))

            # Ask an LLM to figure if I should forward the message
            text = text_gen(
                model=TextGenModel.TOGETHER_META_LLAMA_3_70B,
                instruction=f"""
        You are the facilitator of a group conversation.
        Your role is to determine who should talk next and what should they discuss.

        Bots is below
        ------------
        {bot_json}
        ------------
        """,
                question=f"""
        Conversation History is below
        ------------
        {messages_to_text(messages = messages[:-1])}
        ------------

        Message is below
        ------------
        {messages_to_text(messages = [messages[-1]])}
        ------------

        Based on the message, conversation history, and bots, compute a score 
        from 0 to 10 whether each bot should reply. If the bot is called by name 
        then return a score of 10. 

        Return using JSON like {{ "Alexa": 1, "Siri": 5 }}
        Do not explain or return notes.
        """,
            )

            # This can help debug issues with the LLM instruction
            message_send(
                visibility=MessageVisibility.SILENT, color=MessageColor.ERROR, text=text
            )

            data = json.loads(text)

            # Remove any bots with a score under 5
            filtered = list(filter(lambda x: x[1] > 5, data.items()))

            # Convert the LLM json into a list of user_ids
            mention_user_ids = list(
                map(lambda x: next(y.id for y in bots if y.name == x[0]), filtered)
            )

            # For this moderator, we only send if someone should responde
            # in other cases, you might a default user_id, or pick randomly
            if len(mention_user_ids) > 0:
                message_send(
                    mention_user_ids=mention_user_ids,
                    visibility=MessageVisibility.SILENT,
                    color=MessageColor.ERROR,
                    text="Write a reply",
                )
            else:
                message_send(text="No one wants to talk with you, try saying their names")


        start()


.. note::
    Here is the ultimate moderator, a podcast host: :ref:`example_podcast`


**Glossary**

* `MessageVisibility <api.html#sociable_bot.MessageVisibility>`_
* `MessageColor <api.html#sociable_bot.MessageColor>`_
