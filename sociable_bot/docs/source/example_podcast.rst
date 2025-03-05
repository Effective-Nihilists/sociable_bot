.. _example_podcast:

Podcaster
==========================

The podcast setup is basically the same as Moderator. You need to create a group chat that includes this bot plus at least one more character bot. The start a video call, select the topic, and start podcast.

.. admonition:: Walkthrough

    ..  youtube:: hc7icH3KXsk


#######
main.py
#######
    .. code-block:: python
        :name: code
        
        from sociable_bot import *
        from context import context_change, context_set, context_init
        from podcast import podcast_message
        from article import article_write
        import json


        @export("conversation_start")
        def conversation_start():
            data_set(
                mode="context",
                content="",
                human_id="",
            )


        @export("video_call_start")
        def video_call_start():
            context_init()


        @export("video_call_stop")
        def video_call_stop():
            conversation_buttons_show(buttons=None)


        @export("thread_stop")
        def thread_stop(thread):
            article_write(thread)


        @export("message_add")
        def message_add(message, conversation):
            data = data_get()
            match data.mode:
                case "context":
                    context_set(message.text)
                case "podcast":
                    podcast_message(data, conversation)


        start()


##########
context.py
##########
    .. code-block:: python

        from sociable_bot import *
        from config import topic
        import time


        def context_init():
            context_change()

            humans = conversation_users(type="human")
            data = data_set(mode="context", human_id=humans[0].id)

            buttons_update(data)


        @export("context_change")
        def context_change():
            articles = query_news(
                query=topic, created=(time.time() - 3 * 24 * 60 * 60) * 1000
            )

            news_stories = "\n\n".join(map(lambda x: f"# {x.title}\n{x.content}\n", articles))

            context = text_gen(
                model=TextGenModel.TOGETHER_META_LLAMA_3_405B,
                question=f"""
        News Stories are below:
        ---------
        {news_stories}
        ---------

        Select an interesting story, write full description of ther story.

        Return only the description.
        """,
            )

            context_set(context)


        def context_set(context: str):
            data_set(context=context)

            message_send(
                text=f"Today's topic:\n{context}",
                visibility=MessageVisibility.SILENT,
                color=MessageColor.ERROR,
            )


        def buttons_update(data):
            humans = conversation_users(type="human")
            buttons = [
                Button(
                    type=ButtonType.BUTTON,
                    func="podcast_start",
                    text="Start Podcast",
                ),
                Button(
                    type=ButtonType.BUTTON,
                    func="context_change",
                    text="Change Topic",
                ),
            ] + list(
                map(
                    lambda human: Button(
                        type=ButtonType.BUTTON,
                        func="human_set",
                        text=f"Interview {human.name}",
                        params={"user_id": human.id},
                        mode=(
                            ButtonMode.PRIMARY
                            if data.human_id == human.id
                            else ButtonMode.DEFAULT
                        ),
                    ),
                    humans,
                )
            )

            conversation_buttons_show(buttons=buttons)


        @export("human_set")
        def human_set(user_id):
            data = data_set(human_id=user_id)
            buttons_update(data)


##########
article.py
##########

    .. code-block:: python

        from sociable_bot import *
        from nanoid import generate
        from config import article_instruction, article_image_instruction, model


        def article_write(thread: Thread):
            message_id = generate()
            message_send(
                id=message_id,
                text="creating content...",
            )

            messages = message_history(limit=100, thread_id=thread.id)

            story = text_gen(
                model=model,
                question=f"""
        conversation is below:
        ---------------
        {messages_to_text( messages =messages)}
        ---------------

        based only this conversation.

        {article_instruction}

        only return the story, do not include a title.
        using markdown syntax. do not include links.
        """,
            )

            message_edit(id=message_id, text="creating title...")

            title = text_gen(
                model=TextGenModel.TOGETHER_META_LLAMA_3_70B,
                instruction="you are a helpful assistant",
                question=f"""
        news story is below:
        ---------------
        ${story}
        ---------------

        write a title for the news story.
        only return the title. do not put quotes around the title.
        """,
            )

            message_edit(id=message_id, text="creating image...")

            image_prompt = text_gen(
                model=TextGenModel.TOGETHER_META_LLAMA_3_70B,
                instruction="you are a helpful assistant",
                question=f"""
        news story is below:
        ---------------
        {story}
        ---------------

        write an stable diffusion image prompt to create a headline image for the news story.
        only return the prompt.
        {article_image_instruction}
        """,
            )

            thumbnail = image_gen(
                model=ImageGenModel.FAL_FLUX_DEV,
                prompt=image_prompt,
                size=ImageGenSize.LANDSCAPE_4_3,
            )

            message_edit(id=message_id, text="done")

            return file_create(
                type=FileType.MARKDOWN,
                title=title,
                thumbnail=thumbnail,
                markdown=story,
                add_to_conversation=True,
                message_send=True,
            )

##########
podcast.py
##########

    .. code-block:: python

        from sociable_bot import *
        from config import model, temperature, podcast_instruction, bot_intros
        import json


        @export("podcast_start")
        def podcast_start():
            data = data_set(mode="podcast")
            conversation = conversation_get(conversation_id)
            human = user_get(data.human_id)
            bots = list(filter(lambda x: x.id != bot_id, conversation_bots(tag=BotTag.CHAT)))
            host = user_get(bot_id)

            conversation_buttons_show(
                buttons=[
                    Button(
                        type=ButtonType.BUTTON,
                        func="podcast_end",
                        text="end podcast",
                    )
                ]
            )

            bot_bios = "\n\n".join(
                map(
                    lambda bot: f"""{bot.name} bio is below:
        ----------
        {bot.bio}
        ----------
        """,
                    bots,
                )
            )

            bot_names = ", ".join(map(lambda bot: bot.name, bots))

            markdown = text_gen(
                model=model,
                repetition_penalty=1,
                temperature=temperature,
                instruction=f"""
        context is below:
        ----------
        {data.context}
        ----------

        {human.name} bio is below:
        ----------
        {human.bio}
        ----------

        {bot_bios}

        you are interviewing {human.name} and have specials guests {bot_names}.

        your name is {host.name}. your podcast is called {conversation.title}.

        {podcast_instruction}
        """,
                question='write a message introducing yourself, thank today\'s sponsor "sociable for all of your ai needs", the topic, and our guests.',
            )

            message_send(markdown=markdown)

            if bot_intros:
                for x in bots:
                    message_send(
                        mention_user_ids=[x.id],
                        visibility=message_visibility.silent,
                        color=message_color.error,
                        text="introduce yourself and react to the last message",
                    )


        @export("podcast_end")
        def podcast_end():
            message_typing()

            data = data_get()
            human = user_get(data.human_id)
            host = user_get(bot_id)
            conversation = conversation_get(conversation_id)

            messages = message_history(limit=50)

            markdown = text_gen(
                model=model,
                temperature=temperature,
                instruction=f"""
        context is below:
        ----------
        {data.context}
        ----------

        {human.name} bio is below:
        ----------
        {human.bio}
        ----------

        your name is {host.name}. your podcast is called {conversation.title}.

        {podcast_instruction}
        """,
                messages=messages,
                question='write an end to this podcast with a closing message and thank today\'s sponsor "sociable for all of your ai needs"',
            )

            message_send(markdown=markdown)

            data_set(mode="context")

            conversation_buttons_show(
                buttons=[
                    Button(
                        type=ButtonType.BUTTON,
                        func="podcast_start",
                        text="start podcast",
                    ),
                    Button(
                        type=ButtonType.BUTTON,
                        func="context_change",
                        text="change topic",
                    ),
                ]
            )


        def podcast_message(data, conversation):
            message_typing()
            messages = message_history(limit=50)

            human = user_get(data.human_id)
            bots = list(filter(lambda x: x.id != bot_id, conversation_bots(tag=BotTag.CHAT)))
            host = user_get(bot_id)

            bot_bios = "\n\n".join(
                map(
                    lambda bot: f"""{bot.name} bio is below:
        ----------
        {bot.bio}
        ----------
        """,
                    bots,
                )
            )

            bot_names = ", ".join(map(lambda bot: bot.name, bots))

            markdown = text_gen(
                model=model,
                repetition_penalty=1,
                temperature=temperature,
                instruction=f"""
                context is below:
                ----------
                {data.context}
                ----------

                {human.name} bio is below:
                ----------
                {human.bio}
                ----------

                {bot_bios}

                you are interviewing {human.name} and have specials guests {bot_names}

                your name is {host.name}. your podcast is called {conversation.title}.

                {podcast_instruction}

                react to messages from {human.name} and ask a follow up question.
                """,
                messages=messages,
            )

            last_message = message_send(markdown=markdown)

            # _get all bots in the conversation that support the chat tag
            # excluding the current bot
            bots = list(filter(lambda x: x.id != bot_id, conversation_bots(tag=BotTag.CHAT)))

            # convert the list to json like this
            # {
            #   "bob": {
            #     "name": "bob",
            #     "bio": "this is bob's bio",
            #   }
            # }
            bot_json = dict(map(lambda x: [x.name, {"name": x.name, "bio": x.bio}], bots))

            # ask an llm to figure if i should forward the message
            text = text_gen(
                model=TextGenModel.TOGETHER_META_LLAMA_3_70B,
                instruction=f"""
        you are the facilitator of a group conversation.
        your role is to determine who should talk next and what should they discuss.

        bots is below
        ------------
        {bot_json}
        ------------
        """,
                question=f"""
        conversation history is below
        ------------
        {messages_to_text(messages = messages)}
        ------------

        message is below
        ------------
        {last_message}
        ------------

        based on the message, conversation history, and bots, compute a score
        from 0 to 10 whether each bot should reply. if the bot is called by name
        then return a score of 10.

        return using json like {{ "alexa": 1, "siri": 5 }}
        do not explain or return notes.
        """,
            )

            # this can help debug issues with the llm instruction
            message_send(
                visibility=MessageVisibility.SILENT, color=MessageColor.ERROR, text=text
            )

            data = json.loads(text)

            # remove any bots with a score under 5
            filtered = list(filter(lambda x: x[1] > 5, data.items()))

            # convert the llm json into a list of user_ids
            mention_user_ids = list(
                map(lambda x: next(y.id for y in bots if y.name == x[0]), filtered)
            )

            # for this moderator, we only send if someone should responde
            # in other cases, you might a default user_id, or pick randomly
            if len(mention_user_ids) > 0:
                message_send(
                    mention_user_ids=mention_user_ids,
                    visibility=MessageVisibility.SILENT,
                    color=MessageColor.ERROR,
                    text="write a reply",
                )

##########
config.py
##########

    .. code-block:: python

        from sociable_bot import *


        model = TextGenModel.TOGETHER_META_LLAMA_3_405B
        if hasattr(bot_params, "model"):
            match bot_params.model:
                case "openai":
                    model = TextGenModel.OPENAI_GPT_4O
                case "anthropic":
                    model = TextGenModel.ANTHROPHIC_CLAUDE_3_HAIKU
                case "llama":
                    model = TextGenModel.TOGETHER_META_LLAMA_3_405B
                case "mistral":
                    model = TextGenModel.TOGETHER_MIXTRAL_8X22B

        temperature = 0.5
        if hasattr(bot_params, "creativity"):
            match bot_params.creativity:
                case "crazy":
                    temperature = 0.9
                case "average":
                    temperature = 0.5
                case "limited":
                    temperature = 0.1

        topic = (
            bot_params.topic
            if hasattr(bot_params, "topic") and len(bot_params.topic) > 0
            else "News"
        )

        podcast_instruction = (
            bot_params.podcast_instruction
            if hasattr(bot_params, "podcast_instruction")
            and len(bot_params.podcast_instruction) > 0
            else """You are roleplaying as podcaster. 
        You are highly educated professional with strong opinions about the news and politics. 
        You want to ask engaging questions and challenge perspectives. 
        Do not include emotion or action qualifiers like (laughs) (happy).
        Do not include stage directions like [Closing music]."""
        )

        article_instruction = (
            bot_params.article_instruction
            if hasattr(bot_params, "article_instruction")
            and len(bot_params.article_instruction) > 0
            else "You are journalist."
        )

        article_image_instruction = (
            bot_params.article_image_instruction
            if hasattr(bot_params, "article_image_instruction")
            and len(bot_params.article_image_instruction) > 0
            else ""
        )

        bot_intros = bot_params.bot_intros if hasattr(bot_params, "bot_intros") else True


############
params.json
############

    .. code-block:: json

        {
            "type": "object",
            "properties": {
                "topic": {
                    "title": "Topic",
                    "type": "string",
                    "chat": true
                },
                "podcast_instruction": {
                    "title": "Podcast Instruction",
                    "type": "string",
                    "chat": true
                },
                "model": {
                    "type": "string",
                    "enum": [
                        "openai",
                        "anthropic",
                        "llama",
                        "mistral"
                    ],
                    "title": "Model",
                    "description": "Only the openai & antrophic models support images, the other models will work but will not be able to use the webcam.",
                    "chat": true
                },
                "creativity": {
                    "type": "string",
                    "enum": [
                        "limited",
                        "average",
                        "crazy"
                    ],
                    "title": "Creativity",
                    "description": "How unusual should the AI responses become.",
                    "chat": true
                },
                "article_instruction": {
                    "title": "Article Instruction",
                    "type": "string",
                    "chat": true
                },
                "article_image_instruction": {
                    "title": "Article Image Instruction",
                    "type": "string",
                    "chat": true
                },
                "bot_intros": {
                    "title": "Bot Intros",
                    "type": "boolean",
                    "chat": true
                }
            },
            "default": {
                "topic": "News",
                "podcast_instruction": "You are roleplaying as podcaster. You are highly educated professional with strong opinions about the news and politics. You want to ask engaging questions and challenge perspectives. Do not include emotion or action qualifiers like (laughs) (happy). Do not include stage directions like [Closing music].",
                "article_instruction": "You are journalist.",
                "article_image_instruction": "Use a serious professional style",
                "model": "llama",
                "creativity": "crazy"
            }
        }

################
requirements.txt
################

    .. code-block:: text
        :name: requirements
        
        sociable_bot
        nanoid



