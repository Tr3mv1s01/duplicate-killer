import threading
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List

from src.core.hash_engine import compute_hash
from src.core.scanner import FileInfo
from src.logger.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class DuplicateGroup:
    files: List[FileInfo] = field(default_factory=list)
    total_wasted: int = 0

    @property
    def file_count(self) -> int:
        return len(self.files)


class Analyzer:
    def __init__(self):
        self._stop_event = threading.Event()

    @property
    def stop_event(self) -> threading.Event:
        return self._stop_event

    def stop(self):
        self._stop_event.set()

    def analyze(
        self,
        files: List[FileInfo],
        progress_callback: callable = None,
    ) -> List[DuplicateGroup]:
        self._stop_event.clear()

        size_groups = self._group_by_size(files)
        candidates = {s: g for s, g in size_groups.items() if len(g) > 1}

        total = len(candidates)
        processed = 0
        result = []

        for size_group in candidates.values():
            if self._stop_event.is_set():
                return []

            hash_groups = self._hash_and_group(size_group)

            for hash_value, file_list in hash_groups.items():
                if len(file_list) > 1:
                    wasted = sum(f.size for f in file_list[1:])
                    result.append(DuplicateGroup(files=file_list, total_wasted=wasted))

            processed += 1
            if progress_callback and total > 0:
                progress_callback(processed / total)

        result.sort(key=lambda g: g.total_wasted, reverse=True)
        return result

    def _group_by_size(self, files: List[FileInfo]) -> Dict[int, List[FileInfo]]:
        groups = defaultdict(list)
        for f in files:
            groups[f.size].append(f)
        return dict(groups)

    def _hash_and_group(self, files: List[FileInfo]) -> Dict[str, List[FileInfo]]:
        hash_groups = defaultdict(list)
        for f in files:
            if self._stop_event.is_set():
                return {}
            file_hash = compute_hash(f.path, self._stop_event)
            if not file_hash:
                continue
            f.hash_value = file_hash
            hash_groups[file_hash].append(f)
        return dict(hash_groups)
