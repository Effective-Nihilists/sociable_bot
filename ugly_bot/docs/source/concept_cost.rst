
Cost
==========================

Ugly uses pre-paid charging model. Everyone gets some credit to start out and then they need to add funds to continue to use any of the paid services, covered in detail here:
`Detailed Pricing <https://ugly.bot/pricing>`_

By default the costs of using a bot are divided evenly amongst the owners of a conversations. Unless the bot owner sets the "Billing" field to specifically charge their account.

**Scenarios:**

* Customer Support Bot: I create a new support bot for Bob's shoes and set the "Billing" to use my account. Then any costs associated with using that bot will charge to my acount.
* Group chat with my family: I create a new chat where I am the owner, my family are all members. If anyone uses a bot in this chat it will charge my account.
* Cron / hourly bot: I create a bot with the "cron" tag and I use text_gen inside of the bot_hourly event. This will charge my account. Since the bot is not in a conversation, it assigns all costs to the owner of the bot.

.. note::
    The bots use normal Python and you can include any python package, so it is possible to call OpenAI directly using your own API token. However, there is nothing to prevent other users from using your bot and all of that usage will be charged to your OpenAI account. Also, for security reasons bots that use the internet may not be usable in all situations because we cannot ensure user privacy.