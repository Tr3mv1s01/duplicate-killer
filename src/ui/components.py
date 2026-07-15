import customtkinter as ctk

from src.ui.theme import COLORS, FONTS


class CardFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(corner_radius=12)

    def apply_theme_colors(self, theme: str):
        colors = COLORS[theme]
        self.configure(fg_color=colors["card"], border_color=colors["card_border"])


class ProgressCard(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=12)
        self.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(self, mode="determinate", height=8)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        self.progress_bar.set(0)

        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="ew")
        self.stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.files_label = ctk.CTkLabel(
            self.stats_frame, text="Files scanned: 0", font=FONTS["small"]
        )
        self.files_label.grid(row=0, column=0, padx=4, pady=2, sticky="w")

        self.groups_label = ctk.CTkLabel(
            self.stats_frame, text="Duplicate groups: 0", font=FONTS["small"]
        )
        self.groups_label.grid(row=0, column=1, padx=4, pady=2)

        self.space_label = ctk.CTkLabel(
            self.stats_frame, text="Wasted space: 0 B", font=FONTS["small"]
        )
        self.space_label.grid(row=0, column=2, padx=4, pady=2, sticky="e")

    def update_progress(self, value: float):
        self.progress_bar.set(value)

    def update_stats(self, files: int, groups: int, wasted: str, lang: dict):
        self.files_label.configure(text=lang["files_scanned"].format(files))
        self.groups_label.configure(text=lang["duplicate_groups"].format(groups))
        self.space_label.configure(text=lang["wasted_space"].format(wasted))


class ResultCard(ctk.CTkFrame):
    def __init__(self, master, group_index: int, files: list, wasted: str, lang: dict):
        super().__init__(master, corner_radius=10)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.checkboxes = []

        copies_text = f"{len(files)} {lang['copies']}"
        header_text = f"Group {group_index} — {wasted} ({copies_text})"
        self.header = ctk.CTkLabel(
            self, text=header_text, font=FONTS["heading"],
            anchor="w"
        )
        self.header.grid(row=0, column=0, columnspan=2, padx=12, pady=(8, 4), sticky="w")

        for i, file_info in enumerate(files):
            from src.core.scanner import FileInfo
            if not isinstance(file_info, FileInfo):
                break
            var = ctk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(
                self,
                text="",
                variable=var,
                checkbox_width=18,
                checkbox_height=18,
            )
            cb.grid(row=i + 1, column=0, padx=(12, 4), pady=2, sticky="w")

            name_label = ctk.CTkLabel(
                self,
                text=file_info.path,
                font=FONTS["small"],
                anchor="w",
            )
            name_label.grid(row=i + 1, column=1, padx=(0, 12), pady=2, sticky="w")

            self.checkboxes.append((var, file_info))

        self.bottom_padding = ctk.CTkLabel(self, text="")
        self.bottom_padding.grid(row=len(files) + 1, column=0, columnspan=2, pady=(0, 4))

    def get_selected(self) -> list:
        return [fi for var, fi in self.checkboxes if var.get()]
