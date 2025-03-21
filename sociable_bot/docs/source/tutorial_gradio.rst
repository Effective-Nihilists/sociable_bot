Gradio
==========================

`Example <https://sociable.bot/botEdit?botId=8BqzzLO2xP2bhbFxC9dBf>`_

Many python libraries support running web servers to show interactive UI, like Gradio, Bokeh, Matplotlib. Sociable supports showing this content using a proxy server for HTTP & WebSockets. If you **conversation_content_show** a relative URL like "/" or "/hello" then we will show that content inside an iframe.

.. admonition:: main.py

    Based on https://www.gradio.app/docs/gradio/colorpicker

    .. code-block:: python
        :name: code
        

        from sociable_bot import *

        import gradio as gr
        import numpy as np
        from PIL import Image, ImageColor

        @export("conversation_start")
        def conversation_start():
            conversation_content_show(uri="/")
            # If want the content to take over the entire view, uncomment below
            conversation_content_maximized(True)

        def change_color(icon, color):

            """
            Function that given an icon in .png format changes its color
            Args:
                icon: Icon whose color needs to be changed.
                color: Chosen color with which to edit the input icon.
            Returns:
                edited_image: Edited icon.
            """
            img = icon.convert("LA")
            img = img.convert("RGBA")
            image_np = np.array(icon)
            _, _, _, alpha = image_np.T
            mask = alpha > 0
            image_np[..., :-1][mask.T] = ImageColor.getcolor(color, "RGB")
            edited_image = Image.fromarray(image_np)
            return edited_image

        inputs = [
            gr.Image(label="icon", type="pil", image_mode="RGBA"),
            gr.ColorPicker(label="color"),
        ]
        outputs = gr.Image(label="colored icon")

        demo = gr.Interface(
            fn=change_color,
            inputs=inputs,
            outputs=outputs
        )

        if __name__ == "__main__":
            # Normally, we would call start() which would block,
            # start_nonblocking creates a Thread to process any future
            # events and lets you continue to initialize the web server
            start_nonblocking()
            demo.launch(server_port=bot_port)



.. admonition:: requirements.txt

    .. code-block:: text
        :name: requirements
        
        sociable_bot
        gradio
        numpy
        pillow

**Glossary**

* `conversation_content_show <api.html#sociable_bot.conversation_content_show>`_
* `conversation_content_maximized <api.html#sociable_bot.conversation_content_maximized>`_
* `start_nonblocking <api.html#sociable_bot.start_nonblocking>`_
