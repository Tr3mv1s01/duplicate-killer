import os
import re


def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.1f} MB"
    elif size_bytes < 1024 ** 4:
        return f"{size_bytes / 1024 ** 3:.2f} GB"
    else:
        return f"{size_bytes / 1024 ** 4:.2f} TB"


def format_size_with_unit(size_bytes: int, lang: dict) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} {lang['bytes']}"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} {lang['kb']}"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.1f} {lang['mb']}"
    elif size_bytes < 1024 ** 4:
        return f"{size_bytes / 1024 ** 3:.2f} {lang['gb']}"
    else:
        return f"{size_bytes / 1024 ** 4:.2f} {lang['tb']}"


def get_file_name(file_path: str) -> str:
    return os.path.basename(file_path)


def get_file_extension(file_path: str) -> str:
    _, ext = os.path.splitext(file_path)
    return ext.lower()


def is_copy_filename(file_path: str) -> bool:
    name = os.path.basename(file_path)
    name_no_ext, _ = os.path.splitext(name)
    return bool(re.search(r'\s+\(\d+\)$|\s+-\s+Copy$|^Copy\s+of\s+', name_no_ext))


def get_base_name(file_path: str) -> str:
    name = os.path.basename(file_path)
    name_no_ext, _ = os.path.splitext(name)
    name_no_ext = re.sub(r'\s+\(\d+\)$|\s+-\s+Copy$|^Copy\s+of\s+', '', name_no_ext)
    return name_no_ext.strip()


def sort_duplicate_files(file_paths: list) -> list:
    copies = [p for p in file_paths if is_copy_filename(p)]
    originals = [p for p in file_paths if not is_copy_filename(p)]
    copies.sort(key=lambda p: (get_base_name(p).lower(), p.lower()))
    originals.sort(key=lambda p: p.lower())
    return originals + copies


def is_excluded(file_path: str, excluded_folders: list, excluded_extensions: list) -> bool:
    for folder in excluded_folders:
        if file_path.startswith(folder):
            return True
    ext = get_file_extension(file_path)
    if ext in excluded_extensions:
        return True
    return False
