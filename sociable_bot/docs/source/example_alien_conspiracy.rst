.. _example_alien_conspiracy:

Alien Conspiracy
==========================

This bot will create a post once per day. If you send it the message "post", it will create a new post immediately. The image & text instructions are at the top of source and easy to modify to change the type of content.

.. warning::
    Make sure to add the :ref:`feed and chat tag <concept_export>` to the bot

.. admonition:: main.py

    .. code-block:: python
        :name: code
        
        from sociable_bot import *
        from nanoid import generate
        import time

        instruction = (
            "Write a news story about how this was caused by a secret alien conspiracy"
        )
        query = "News"
        image_instruction= "Make everything look like an alien conspiracy using a dark sci-fi style"


        def create_post(add_to_conversation: bool, query: str):
            data = data_get()

            message_id = generate()
            if add_to_conversation:
                message_send(id=message_id, text="Searching news...")

            news = query_news(query=query, created=(time.time() - 24 * 60 * 60) * 1000, limit=20)

            if add_to_conversation:
                message_edit(id=message_id, text="Selecting story...")

            recent_news_stories_text = "\n\n".join(map(lambda x: x.content, news))
            previous_news_stories_text = "\n\n".join(data.previous_stories)

            news_story = text_gen(
                model=TextGenModel.TOGETHER_META_LLAMA_3_70B,
                question=f"""
        Recent News Stories are below:
        --------------
        {recent_news_stories_text}
        --------------

        Previous News Stories are below:
        --------------
        {previous_news_stories_text}
        --------------

        Based on the Recent News Stories, and the query "{query}" select the most interesting news story that is different from previous news stories. 
        Do not select a story that is too similar to previous news stories.

        Return the only one story. Do not mention other interesting stories.

        Using markdown syntax, include clickable links to the relevant news stories.
        """,
            )

            data = data_set(previous_stories=([news_story] + data.previous_stories)[:10])

            if add_to_conversation:
                message_edit(id=message_id, text="Creating content...")

            story = text_gen(
                model=TextGenModel.TOGETHER_META_LLAMA_3_70B,
                question=f"""
        News Story is below:
        ---------------
        {news_story}
        ---------------

        Based on only this News Story, and the query "{query}".

        {instruction}

        Only return the story, do not include a title.
        Using markdown syntax, include clickable links to the relevant news stories.
        """,
            )

            if add_to_conversation:
                message_edit(id=message_id, text="Creating title...")

            title = text_gen(
                model=TextGenModel.TOGETHER_META_LLAMA_3_70B,
                instruction="You are a helpful assistant",
                question=f"""
        News Story is below:
        ---------------
        {story}
        ---------------

        Write a title for the News Story.
        Only return the title. Do not put quotes around the title.
        """,
            )

            if add_to_conversation:
                message_edit(id=message_id, text="Creating image...")

            image_prompt = text_gen(
                model=TextGenModel.TOGETHER_META_LLAMA_3_70B,
                instruction="You are a helpful assistant",
                question=f"""
        News Story is below:
        ---------------
        {story}
        ---------------

        Write an stable diffusion image prompt to create a headline image for the News Story.
        Only return the prompt.
        {image_instruction}
        """,
            )

            thumbnail = image_gen(
                model=ImageGenModel.FAL_FLUX_DEV,
                prompt=image_prompt,
                size=ImageGenSize.LANDSCAPE_4_3,
            )

            if add_to_conversation:
                message_edit(id=message_id, text="Done")

            return file_create(
                type=FileType.MARKDOWN,
                title=title,
                thumbnail=thumbnail,
                markdown=story,
                add_to_conversation=add_to_conversation,
                add_to_feed=not add_to_conversation,
                message_send=add_to_conversation,
            )


        @export("search_news")
        def search_news(query: str):
            news = query_news(
                query=query, created=(time.time() - 24 * 60 * 60) * 1000, limit=20
            )

            return "\n\n".join(map(lambda x: f"[{x.title}]({x.uri})\n{x.content}", news))


        tool_search_news = TextGenTool(
            name="search_news",
            description="Search News",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for news"}
                },
                "required": ["query"],
            },
        )


        @export("message_direct")
        def message_direct(message):
            if message.text == "post":
                create_post(True, query=query)
                return

            message_typing()
            text = text_gen(
                model=TextGenModel.OPENAI_GPT_4O,
                tools=[tool_search_news],
                instruction=instruction,
                messages=message_history(duration=24 * 60 * 60 * 1000, limit=500),
            )

            message_send(markdown=text)


        @export("bot_hourly")
        def bot_hourly(hour):
            if hour != 12:
                return

            create_post(False, query=query)


        @export("conversation_hourly")
        def conversation_hourly(hour, conversation):
            if hour != 12:
                return

            if conversation.type != ConversationType.GROUP:
                return

            create_post(True, query=query)


        @export("conversation_start")
        def init():
            data_set(previous_stories=[])


        start()


.. admonition:: requirements.txt

    .. code-block:: text
        :name: requirements
        
        sociable_bot
        nanoid



