import os
from tkinter import filedialog
from typing import List

import customtkinter as ctk

from src.io.config import Config
from src.ui.theme import FONTS
from src.utils.constants import STRINGS


class ConfirmDeleteDialog(ctk.CTkToplevel):
    def __init__(self, parent, file_count: int, wasted_text: str, lang: dict):
        super().__init__(parent)
        self.confirmed = False
        self.title(lang["confirm_delete_title"])
        self.geometry("480x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        msg = lang["confirm_delete_msg"].format(file_count, wasted_text)
        label = ctk.CTkLabel(
            self, text=msg, font=FONTS["body"], wraplength=440, justify="left"
        )
        label.grid(row=0, column=0, padx=24, pady=(24, 12))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=1, column=0, pady=(0, 16))
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        cancel_btn = ctk.CTkButton(
            btn_frame, text=lang["cancel"],
            command=self._cancel, width=120
        )
        cancel_btn.grid(row=0, column=0, padx=8)

        confirm_btn = ctk.CTkButton(
            btn_frame, text=lang["confirm"],
            command=self._confirm, width=120
        )
        confirm_btn.grid(row=0, column=1, padx=8)

        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.wait_window()

    def _confirm(self):
        self.confirmed = True
        self.destroy()

    def _cancel(self):
        self.confirmed = False
        self.destroy()


class ErrorDialog(ctk.CTkToplevel):
    def __init__(self, parent, title: str, message: str, lang: dict):
        super().__init__(parent)
        self.title(title)
        self.geometry("460x160")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)

        label = ctk.CTkLabel(
            self, text=message, font=FONTS["body"],
            wraplength=420, justify="left"
        )
        label.grid(row=0, column=0, padx=24, pady=(24, 12))

        close_btn = ctk.CTkButton(
            self, text=lang["close"],
            command=self.destroy, width=120
        )
        close_btn.grid(row=1, column=0, pady=(0, 16))

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window()


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, config: Config, lang: dict):
        super().__init__(parent)
        self.config = config
        self.lang = lang
        self.result = None

        self.title(lang["settings_title"])
        self.geometry("520x400")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._save)
        self.wait_window()

    def _build_ui(self):
        theme_frame = ctk.CTkFrame(self, fg_color="transparent")
        theme_frame.grid(row=0, column=0, padx=24, pady=(16, 4), sticky="ew")
        theme_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(theme_frame, text=self.lang["theme"], font=FONTS["body"]).grid(
            row=0, column=0, sticky="w"
        )
        self.theme_var = ctk.StringVar(value=self.config.theme)
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=[self.lang["dark"], self.lang["light"]],
            command=self._on_theme_change,
        )
        theme_menu.grid(row=0, column=1, sticky="e")
        theme_menu.set(self.lang["dark"] if self.config.theme == "dark" else self.lang["light"])

        lang_frame = ctk.CTkFrame(self, fg_color="transparent")
        lang_frame.grid(row=1, column=0, padx=24, pady=4, sticky="ew")
        lang_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(lang_frame, text=self.lang["language"], font=FONTS["body"]).grid(
            row=0, column=0, sticky="w"
        )
        self.lang_var = ctk.StringVar(value=self.config.language)
        lang_menu = ctk.CTkOptionMenu(
            lang_frame, values=["English", "Русский"],
            command=self._on_lang_change,
        )
        lang_menu.grid(row=0, column=1, sticky="e")
        lang_menu.set("English" if self.config.language == "en" else "Русский")

        notebook = ctk.CTkTabview(self)
        notebook.grid(row=2, column=0, padx=24, pady=8, sticky="nsew")

        folders_tab = notebook.add(self.lang["excluded_folders"])
        folders_tab.grid_columnconfigure(0, weight=1)
        folders_tab.grid_rowconfigure(0, weight=1)

        self.folders_text = ctk.CTkTextbox(folders_tab, height=80, font=FONTS["small"])
        self.folders_text.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        for f in self.config.excluded_folders:
            self.folders_text.insert("end", f + "\n")

        folders_btn_frame = ctk.CTkFrame(folders_tab, fg_color="transparent")
        folders_btn_frame.grid(row=1, column=0, pady=(0, 8))

        ctk.CTkButton(
            folders_btn_frame, text=self.lang["remove"],
            command=lambda: self._remove_selected(self.folders_text),
            width=80,
        ).pack(side="left", padx=4)

        exts_tab = notebook.add(self.lang["excluded_extensions"])
        exts_tab.grid_columnconfigure(0, weight=1)
        exts_tab.grid_rowconfigure(0, weight=1)

        self.exts_text = ctk.CTkTextbox(exts_tab, height=80, font=FONTS["small"])
        self.exts_text.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        for e in self.config.excluded_extensions:
            self.exts_text.insert("end", e + "\n")

        exts_btn_frame = ctk.CTkFrame(exts_tab, fg_color="transparent")
        exts_btn_frame.grid(row=1, column=0, pady=(0, 8))

        ctk.CTkButton(
            exts_btn_frame, text=self.lang["remove"],
            command=lambda: self._remove_selected(self.exts_text),
            width=80,
        ).pack(side="left", padx=4)

        save_btn = ctk.CTkButton(
            self, text=self.lang["save"],
            command=self._save, width=120
        )
        save_btn.grid(row=3, column=0, pady=(0, 16))

    def _on_theme_change(self, choice: str):
        new_theme = "light" if choice == self.lang["light"] else "dark"
        self.config.theme = new_theme

    def _on_lang_change(self, choice: str):
        new_lang = "en" if choice == "English" else "ru"
        self.config.language = new_lang

    def _remove_selected(self, textbox: ctk.CTkTextbox):
        try:
            sel = textbox.selection_get()
            textbox.delete("sel.first", "sel.last")
        except (ctk.TclError, Exception):
            pass

    def _save(self):
        folders = [
            l.strip()
            for l in self.folders_text.get("1.0", "end").strip().split("\n")
            if l.strip()
        ]
        exts = [
            l.strip().lower()
            for l in self.exts_text.get("1.0", "end").strip().split("\n")
            if l.strip()
        ]
        self.config.excluded_folders = folders
        self.config.excluded_extensions = exts
        self.config.save()
        self.destroy()


def choose_folder_dialog(lang: dict) -> str:
    return filedialog.askdirectory(title=lang["choose_folder"])


def choose_save_file_dialog(title: str, file_types: list) -> str:
    return filedialog.asksaveasfilename(title=title, filetypes=file_types)
