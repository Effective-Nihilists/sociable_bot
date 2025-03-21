.. _example_mr_web:

Mr. Web
==========================

`Example <https://sociable.bot/botEdit?botId=idlXnAHKbn45PwrJWOuua>`_

This takes the basic web tutorial much further into a useful tool.

.. admonition:: Walkthrough

    ..  youtube:: Jnixc0lIbGQ

.. warning::
    This bot needs **video** and **web** tags to fully work. The bot's custom context menu is only available if the side panel is open and you are in chat with this bot.

#######
main.py
#######
    .. code-block:: python
        :name: code
        
        from sociable_bot import *
        import html2text


        @export("web_page_updated")
        def web_page_updated(session_id: str, title: str):
            data = data_get()
            if data.auto_context:
                context = context_get(session_id=session_id, selection_text=None)
                data_set(context=context)
                message_send(text=f"Context updated: {title}", visibility=MessageVisibility.SILENT, color=MessageColor.ACCENT)


        def context_get(session_id, selection_text=None):
            if selection_text is not None:
                return selection_text

            page = web_page_get(session_id=session_id)
            return html2text.html2text(page.html)


        @export("context_set")
        def context_set(session_id, selection_text=None):
            context = context_get(session_id=session_id, selection_text=selection_text)
            data = data_set(context=context)
            if data.auto_context:
                data = data_set(auto_context=False)
                menu_update(data)
            message_send(text="Context updated manually", visibility=MessageVisibility.SILENT, color=MessageColor.ACCENT)


        @export("explain")
        def explain(session_id, selection_text=None):
            message_typing()
            context = context_get(session_id=session_id, selection_text=selection_text)
            markdown = text_gen(
                model=TextGenModel.TOGETHER_META_LLAMA_3_70B,
                question=f"""
        Context is below:
        ----------
        {context}
        ----------

        Explain this context in simple terms.
        """,
            )
            message_send(markdown=markdown)


        @export("critique")
        def critique(session_id, selection_text=None):
            message_typing()
            context = context_get(session_id=session_id, selection_text=selection_text)
            markdown = text_gen(
                model=TextGenModel.TOGETHER_META_LLAMA_3_70B,
                question=f"""
        Context is below:
        ----------
        {context}
        ----------

        Explain why this context is wrong, poorly written and just a bad idea.
        """,
            )
            message_send(markdown=markdown)


        @export("explain")
        def explain(session_id, selection_text=None):
            message_typing()
            context = context_get(session_id=session_id, selection_text=selection_text)
            markdown = text_gen(
                model=TextGenModel.TOGETHER_META_LLAMA_3_70B,
                question=f"""
        Context is below:
        ----------
        {context}
        ----------

        Explain this context in simple terms.
        """,
            )
            message_send(markdown=markdown)


        @export("auto_context_toggle")
        def auto_context_toggle():
            data = data_get()
            data = data_set(auto_context=not data.auto_context)
            menu_update(data)


        @export("conversation_start")
        def init():
            data = data_set(auto_context=False, context="")
            menu_update(data)


        def menu_update(data):
            auto_update = "Enabled" if data.auto_context else "Disabled"
            conversation_context_menu_set(
                menu_items=[
                    MenuItem(func="explain", title="Explain"),
                    MenuItem(func="critique", title="Critique"),
                    MenuItem(func="context_set", title="Set Context"),
                    MenuItem(
                        func="auto_context_toggle",
                        title=f"Auto-Update Context: {auto_update}",
                    ),
                ]
            )


        @export("message_direct")
        def send(message):
            data = data_get()
            messages = message_history(limit=50)

            markdown = text_gen(
                model=TextGenModel.TOGETHER_META_LLAMA_3_70B,
                instruction=f"""
        Context is below:
        ----------
        {data.context}
        ----------

        Use this context to answer questions
        """,
                messages=messages,
            )

            message_send(markdown=markdown)


        start()


################
requirements.txt
################

    .. code-block:: text
        :name: requirements
        
        sociable_bot
        html2text



