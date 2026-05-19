import asyncio
import time
from typing import Dict, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from ..config import config

class DebouncedQueue:
    def __init__(self, delay_ms: int = None):
        self.delay = (delay_ms or config.DEBOUNCE_DELAY_MS) / 1000
        self.queue: Dict[str, str] = {}
        self.last_process_time = 0

    def add(self, file_path: str, event_type: str):
        self.queue[file_path] = event_type

    async def process(self, callback: Callable):
        while True:
            await asyncio.sleep(self.delay)

            if self.queue:
                events = self.queue.copy()
                self.queue.clear()

                for path, event_type in events.items():
                    await callback(path, event_type)

class FileWatcher(FileSystemEventHandler):
    def __init__(self, callback: Callable):
        self.callback = callback
        super().__init__()

    def on_modified(self, event: FileSystemEvent):
        if not event.is_directory:
            self.callback(event.src_path, 'modified')

    def on_created(self, event: FileSystemEvent):
        if not event.is_directory:
            self.callback(event.src_path, 'created')

    def on_deleted(self, event: FileSystemEvent):
        if not event.is_directory:
            self.callback(event.src_path, 'deleted')

class WatcherService:
    def __init__(self):
        self.observers: Dict[int, Observer] = {}
        self.debounce_queue = DebouncedQueue()

    def start_watching(self, project_id: int, project_path: str, callback: Callable):
        if project_id in self.observers:
            self.stop_watching(project_id)

        event_handler = FileWatcher(
            lambda path, event_type: self.debounce_queue.add(path, event_type)
        )

        observer = Observer()
        observer.schedule(event_handler, project_path, recursive=True)
        observer.start()

        self.observers[project_id] = observer

    def stop_watching(self, project_id: int):
        if project_id in self.observers:
            self.observers[project_id].stop()
            self.observers[project_id].join()
            del self.observers[project_id]

    def stop_all(self):
        for observer in list(self.observers.values()):
            observer.stop()
            observer.join()
        self.observers.clear()

watcher_service = WatcherService()
