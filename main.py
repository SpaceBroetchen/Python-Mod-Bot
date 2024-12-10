import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import discord
from dotenv import load_dotenv


class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print("File has been modified")
        if not event.is_directory:
            with open('/factorio/logs/console.log') as f:
                for line in f:
                    pass
                last_line = line
            print(last_line)
            client = discord.Client()
            load_dotenv()
            TOKEN = os.getenv('DISCORD_TOKEN')
            client.run(TOKEN)
            channel = client.get_channel("1315700405430128730")
            await channel.send(last_line)

if __name__ == "__main__":
    print("Started")

    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path='/factorio/logs/console.log', recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
