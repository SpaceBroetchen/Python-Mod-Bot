import asyncio
import re
from io import BytesIO

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import discord
import datetime
from configImport import *
import colorGenerator

global observer



COLOR_REGEX = re.compile("^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} \[COLOR] [a-zA-Z0-9_-]+'s color is now (#[0-9A-F]{3,6}|[0-9]{1,3} [0-9]{1,3} [0-9]{1,3}|default|red|green|blue|orange|yellow|pink|purple|white|black|gray|brown|cyan|acid).$")
COLOR_REGEX_SHORT = re.compile("(?<= )(#[0-9A-F]{3,6}|[0-9]{1,3} [0-9]{1,3} [0-9]{1,3}|default|red|green|blue|orange|yellow|pink|purple|white|black|gray|brown|cyan|acid)(?=.)")


def format_message(message):
    splt = message.split("[")
    unix_timestamp = int(datetime.datetime.strptime(splt[0], "%Y-%m-%d %H:%M:%S ").timestamp())
    return f"<t:{unix_timestamp}:f>`[{'['.join(splt[1:])}`"


class MyClient(discord.Client):
    async def on_log_updated(self, message):
        channel = self.get_channel(LOG_CHANNEL_ID)
        if COLOR_REGEX.match(message) != None:
            m = COLOR_REGEX_SHORT.search(message)
        else:
            m = None
        if m is not None:
            image = colorGenerator.generateImage(m.group())
            if image is not None:
                with BytesIO() as im:
                    image.save(im, "PNG")
                    im.seek(0)
                    await channel.send(format_message(message), file=discord.File(fp=im, filename="image.png"))
                return

        await channel.send(format_message(message))

    async def on_ready(self):
        channel = self.get_channel(LOG_CHANNEL_ID)

        global observer
        event_handler = MyHandler(self)
        observer.schedule(event_handler, path=LOG_FILE, recursive=True)
        observer.start()

        await channel.send("The Mod Log bot listens...")



class MyHandler(FileSystemEventHandler):
    def __init__(self, client):
        self.client = client

    def on_modified(self, event):
        print("File has been modified")
        if not event.is_directory:
            with open(LOG_FILE) as f:
                for line in f:
                    pass
                last_line = line

            for i in LOG_KEYWORDS:
                if i in last_line:
                    client.dispatch("log_updated", last_line)
                    break


            print(last_line)


if __name__ == "__main__":
    observer = Observer()
    asyncio.get_event_loop().create_task(fire())

    client = MyClient(intents=discord.Intents.default())
    client.run(TOKEN)
    observer.stop()
    observer.join()
