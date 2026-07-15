import hashlib
import os
import threading

from src.utils.constants import CHUNK_SIZE

_HASH_ALGORITHM = "md5"


def compute_hash(
    file_path: str,
    stop_event: threading.Event = None,
    progress_callback: callable = None,
) -> str:
    hasher = hashlib.new(_HASH_ALGORITHM)
    file_size = os.path.getsize(file_path)
    bytes_read = 0

    try:
        with open(file_path, "rb") as f:
            while True:
                if stop_event and stop_event.is_set():
                    return ""
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                hasher.update(chunk)
                bytes_read += len(chunk)
                if progress_callback and file_size > 0:
                    progress_callback(bytes_read / file_size)
    except (OSError, PermissionError):
        return ""

    return hasher.hexdigest()
