Matplotlib
==========================

`Example <https://ugly.bot/botEdit?botId=QUlcVa8kw5kt9J-fgUhMy>`_


.. admonition:: main.py

    .. code-block:: python
        :name: code
        

        from ugly_bot import *

        import matplotlib.pyplot as plt
        from io import BytesIO


        @export("message_direct")
        def message_direct():
            fig, ax = plt.subplots()

            fruits = ["apple", "blueberry", "cherry", "orange"]
            counts = [40, 100, 30, 55]
            bar_labels = ["red", "blue", "_red", "orange"]
            bar_colors = ["tab:red", "tab:blue", "tab:red", "tab:orange"]

            ax.bar(fruits, counts, label=bar_labels, color=bar_colors)

            ax.set_ylabel("fruit supply")
            ax.set_title("Fruit supply by kind and color")
            ax.legend(title="Fruit color")

            buf = BytesIO()
            plt.savefig(buf, format="jpg")

            message_send(image=Image(buffer=buf.getbuffer()))


        start()


.. admonition:: requirements.txt

    .. code-block:: text
        :name: requirements
        
        ugly_bot
        matplotlib


**Glossary**

* `message_send <api.html#ugly_bot.message_send>`_
