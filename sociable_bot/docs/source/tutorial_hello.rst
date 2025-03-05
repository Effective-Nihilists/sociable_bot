.. _tutorial_hello:

Hello World
==========================

In this simple example, the bot will send a message every time a new conversation is started. You can restart your conversation by selecting "Wipe" from "..." in a conversation.

Steps:

#. Create bot

    #. Open https://sociable.bot
    #. Click on bots
    #. Click on "+" in top-right
    #. Change template to "Custom Python Code"
    #. Click on "Create Bot"

#. Set tag

    #. Click on the box under "Tags" (it should say None)
    #. Select "chat"

#. Update main.py

    #. Click on "Code" tab
    #. Replace the contents of main.py with the text from below
    #. It will auto-save your changes immediately

#. Open chat

    #. Click on "Settings" tab
    #. Click on "Chat" button in the bottom bar
    #. The event "conversation_start" happens when some starts a new conversation with this bot, if you want to restart your conversation click on "..." in the top-right and select "Wipe"

.. admonition:: Walkthrough
    
    ..  youtube:: LXu6ZKLkrHs


.. admonition:: main.py

    .. code-block:: python
        :name: code
        
        from sociable_bot import *

        @export("conversation_start")
        def hello_world():
            message_send(text="Hello World")

        start()