import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import discord
from dotenv import load_dotenv
import os

class MyClient(discord.Client):
    async def on_log_updated(message):
        channel = client.get_channel("1315700405430128730")
        await channel.send(message)
    async def on_ready(self):
        channel = client.get_channel("1315700405430128730")
        print(self.status)
        await channel.send("Der Log bot arbeitet....")  

class MyHandler(FileSystemEventHandler):
    def __init__(self, client):    
        self.client = client

    def on_modified(self, event):
        print("File has been modified")
        if not event.is_directory:
            with open('/factorio/logs/console.log') as f:
                for line in f:
                    pass
                last_line = line
            print(last_line)
            client.dispatch("on_log_updated", last_line)

if __name__ == "__main__":
    print("Started")
    
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    client = MyClient(intents=discord.Intents.default())
    client.run(TOKEN)
    print(client.status)
    print("Hello")
    event_handler = MyHandler(client)
    observer = Observer()
    observer.schedule(event_handler, path='/factorio/logs/console.log', recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
