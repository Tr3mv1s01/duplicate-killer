import csv
import os
from typing import List

from src.core.analyzer import DuplicateGroup
from src.utils.helpers import format_size


class ExportManager:
    def export_txt(self, groups: List[DuplicateGroup], file_path: str):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"Duplicate Killer Report\n")
            f.write(f"{'=' * 60}\n\n")
            for i, group in enumerate(groups, 1):
                f.write(f"Group {i} — {format_size(group.total_wasted)} wasted\n")
                f.write(f"{'-' * 40}\n")
                for file_info in group.files:
                    f.write(f"{format_size(file_info.size)} | {file_info.path}\n")
                f.write("\n")
            total = sum(g.total_wasted for g in groups)
            f.write(f"{'=' * 60}\n")
            f.write(f"Total groups: {len(groups)}\n")
            f.write(f"Total wasted: {format_size(total)}\n")

    def export_csv(self, groups: List[DuplicateGroup], file_path: str):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Group", "File", "Size", "Path"])
            for i, group in enumerate(groups, 1):
                for file_info in group.files:
                    writer.writerow([
                        i,
                        os.path.basename(file_info.path),
                        file_info.size,
                        file_info.path,
                    ])
