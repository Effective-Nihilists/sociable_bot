Bokeh
==========================

`Example <https://sociable.bot/botEdit?botId=QarpudpQ7_EXFjKX3JDlO>`_

Many python libraries support running web servers to show interactive UI, like Gradio, Bokeh, Matplotlib. Sociable supports showing this content using a proxy server for HTTP & WebSockets. If you **conversation_content_show** a relative URL like "/" or "/hello" then we will show that content inside an iframe.

.. admonition:: Walkthrough
    
    ..  youtube:: oyyM-BGXnJY

.. admonition:: main.py

    Based on https://github.com/bokeh/bokeh/blob/3.6.1/examples/server/api/standalone_embed.py

    .. code-block:: python
        :name: code
        

        from sociable_bot import *

        from bokeh.layouts import column
        from bokeh.models import ColumnDataSource, Slider, Div, GlobalImportedStyleSheet
        from bokeh.plotting import figure
        from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature
        from bokeh.server.server import Server
        from bokeh.themes import Theme
        from tornado.web import StaticFileHandler
        import os


        @export("conversation_start")
        def conversation_start():
            conversation_content_show(uri="/")
            # If want the content to take over the entire view, uncomment below
            # conversation_content_maximized(True)


        def bkapp(doc):
            df = sea_surface_temperature.copy()
            source = ColumnDataSource(data=df)

            plot = figure(
                x_axis_type="datetime",
                y_range=(0, 25),
                y_axis_label="Temperature (Celsius)",
                title="Sea Surface Temperature at 43.18, -70.43",
                sizing_mode="stretch_both",
            )
            plot.line("time", "temperature", source=source)

            def callback(attr, old, new):
                if new == 0:
                    data = df
                else:
                    data = df.rolling(f"{new}D").mean()
                source.data = ColumnDataSource.from_df(data)

            slider = Slider(start=0, end=30, value=0, step=1, title="Smoothing by N Days")
            slider.on_change("value", callback)

            # The default stylesheet for Bokeh does not set the 
            # background color and does not block iOS from doing
            # back swiping
            stylesheet = GlobalImportedStyleSheet(url="asset/main.css")
            
            doc.add_root(
                column(
                    children=[slider, plot],
                    sizing_mode="stretch_both",
                    stylesheets=[stylesheet],
                )
            )

            doc.theme = "dark_minimal"

        # Sociable will proxy all HTTP & WebSocket requests to the provided bot_port
        # Static file serving does not work with the Server api, so we use the
        # extra_patterns to server the asset folder, which is used to store our
        # custom CSS
        server = Server(
            {"/": bkapp},
            port=bot_port,
            extra_patterns=[
                (
                    r"/asset/(.*)",
                    StaticFileHandler,
                    {"path": os.path.normpath(os.path.dirname(__file__) + "/asset")},
                )
            ],
        )
        server.start()


        if __name__ == "__main__":
            # Normally, we would call start() which would block,
            # start_nonblocking creates a Thread to process any future
            # events and lets you continue to initialize the web server
            start_nonblocking()
            server.io_loop.start()


.. admonition:: asset/main.css

    .. code-block:: css
        :name: css
        
        html,
        body {
            width: 100%;
            -webkit-overflow-scrolling: touch;
            margin: 0px;
            padding: 0px;
            min-height: 100%;
            background-color: black;
            color: white;
        }


.. admonition:: requirements.txt

    .. code-block:: text
        :name: requirements
        
        sociable_bot
        bokeh
        bokeh_sampledata


**Glossary**

* `conversation_content_show <api.html#sociable_bot.conversation_content_show>`_
* `conversation_content_maximized <api.html#sociable_bot.conversation_content_maximized>`_
* `start_nonblocking <api.html#sociable_bot.start_nonblocking>`_
