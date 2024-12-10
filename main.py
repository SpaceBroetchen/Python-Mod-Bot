import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print("File has been modified")
        if (!event.is_directory):
            with open('/factorio/logs/console.log') as f:
                for line in f:
                    pass
                last_line = line

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
