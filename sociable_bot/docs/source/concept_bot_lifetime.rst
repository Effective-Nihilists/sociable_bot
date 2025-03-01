.. _concept_bot_lifetime:

Bot Lifetime
==========================

A bot is python program running its own venv. There is one instance of this program running for every conversation where the bot is active.

The bot program will end:
* After 5 minutes of not receiving any exported function calls
* During a rolling upgrade of the backend infra
* An exception is not caught
* Bot code is web_page_updated
* Resource constraint issue in the backend infra (out of memory, auto-scaling, etc)

In the event your bot dies, the next function call will automatically create a new instance. If you need to run cron tasks, then use the "cron" tag and bot_hourly export.

.. warning ::
    Do not use global vars for anything critical, use :ref:`tutorial_data` to store anything that needs to survive the bot being restarted.