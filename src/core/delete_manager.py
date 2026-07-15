from dataclasses import dataclass, field
from typing import List

from src.logger.logger import setup_logger

logger = setup_logger(__name__)


class Send2TrashUnavailableError(Exception):
    pass


try:
    from send2trash import send2trash as _send2trash
    _SEND2TRASH_AVAILABLE = True
except ImportError:
    _SEND2TRASH_AVAILABLE = False


@dataclass
class DeleteResult:
    success_count: int = 0
    fail_count: int = 0
    failed_files: List[str] = field(default_factory=list)


class DeleteManager:
    def delete_files(self, file_paths: List[str]) -> DeleteResult:
        result = DeleteResult()
        for path in file_paths:
            try:
                self._delete_single(path)
                result.success_count += 1
            except (OSError, PermissionError) as e:
                logger.error(f"Failed to delete {path}: {e}")
                result.fail_count += 1
                result.failed_files.append(path)
        return result

    def _delete_single(self, file_path: str):
        if _SEND2TRASH_AVAILABLE:
            _send2trash(file_path)
        else:
            import os
            os.remove(file_path)
            logger.warning(f"send2trash unavailable, permanently deleted: {file_path}")

    @property
    def can_use_trash(self) -> bool:
        return _SEND2TRASH_AVAILABLE
