Image Gen
==========================

Now, let's make some "art".

.. warning::
    Make sure you understand how to create a bot from :ref:`tutorial_hello` tutorial

.. admonition:: main.py

    .. code-block:: python
        :name: code
        
        from sociable_bot import *

        @export("message_direct")
        def image_gen_example(message):
            image = image_gen(
                model=ImageGenModel.FAL_FLUX_DEV,
                prompt=message.text
            )
            message_send(image=image)

        start()

**Glossary**

* `ImageGenModel <api.html#sociable_bot.ImageGenModel>`_
* `image_gen <api.html#sociable_bot.image_gen>`_
* `message_send <api.html#sociable_bot.message_send>`_