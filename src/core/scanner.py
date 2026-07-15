import os
import threading
from dataclasses import dataclass, field
from queue import Queue
from typing import List

from src.utils.helpers import is_excluded


@dataclass
class FileInfo:
    path: str
    size: int
    hash_value: str = ""


@dataclass
class ScanResult:
    files: List[FileInfo] = field(default_factory=list)
    total_files: int = 0
    total_size: int = 0
    errors: List[str] = field(default_factory=list)


class Scanner:
    def __init__(self):
        self._stop_event = threading.Event()
        self._queue: Queue = Queue()
        self._thread: threading.Thread = None

    @property
    def queue(self) -> Queue:
        return self._queue

    @property
    def stop_event(self) -> threading.Event:
        return self._stop_event

    def start_scan(
        self,
        root_path: str,
        excluded_folders: List[str] = None,
        excluded_extensions: List[str] = None,
    ):
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._scan_worker,
            args=(root_path, excluded_folders or [], excluded_extensions or []),
            daemon=True,
        )
        self._thread.start()

    def stop(self):
        self._stop_event.set()

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def _scan_worker(
        self,
        root_path: str,
        excluded_folders: List[str],
        excluded_extensions: List[str],
    ):
        files = []

        for dirpath, dirnames, filenames in os.walk(root_path):
            if self._stop_event.is_set():
                return

            dirnames[:] = [
                d for d in dirnames
                if not is_excluded(
                    os.path.join(dirpath, d), excluded_folders, excluded_extensions
                )
            ]

            for filename in filenames:
                if self._stop_event.is_set():
                    return

                file_path = os.path.join(dirpath, filename)

                if is_excluded(file_path, excluded_folders, excluded_extensions):
                    continue

                try:
                    file_size = os.path.getsize(file_path)
                    if file_size == 0:
                        continue
                    files.append(FileInfo(path=file_path, size=file_size))
                    self._queue.put(("file_found", file_path))
                except (OSError, PermissionError) as e:
                    self._queue.put(("error", str(e)))

        self._queue.put(("scan_complete", files))
