Web Page
==========================

Let's create a bot that will complain about the news. This bot requires a new Python package dependency which is handled by updating requirements.txt file.

.. warning::
    Make sure to add the :ref:`web tag <concept_export>` to the bot

    Add install the chrome extension `here <https://chromewebstore.google.com/detail/sociable/haodmoihodngjigfdbojjnohohndoopp>`_

.. admonition:: Walkthrough
    
    ..  youtube:: oyyM-BGXnJY

.. admonition:: main.py

    .. code-block:: python
        :name: code
        
        from sociable_bot import *
        import html2text

        @export("web_page_updated")
        def web_page_updated(session_id: str, title: str):
            message_send(text = f"Viewing {title}")
            message_typing()
            page = web_page_get(session_id = session_id)
            text = html2text.html2text(page.html)
            markdown = text_gen(
                model = TextGenModel.TOGETHER_META_LLAMA_3_70B,
                question = f"""
                Webpage text is below:
                -------
                {text}
                -------

                If this webpage is a news story, explain in detail why it is wrong
                """
            )
            message_send(markdown = markdown)


        start()

.. admonition:: requirements.txt

    .. code-block:: text
        :name: requirements
        
        sociable_bot
        html2text


**Glossary**

* `message_typing <api.html#sociable_bot.message_typing>`_
* `text_gen <api.html#sociable_bot.text_gen>`_
* `message_send <api.html#sociable_bot.message_send>`_
* `web_page_get <api.html#sociable_bot.web_page_get>`_
* `TextGenModel <api.html#sociable_bot.TextGenModel>`_
