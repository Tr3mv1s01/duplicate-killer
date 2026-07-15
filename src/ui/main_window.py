import os
import threading
from queue import Empty
from typing import List

import customtkinter as ctk

from src.core.analyzer import Analyzer, DuplicateGroup
from src.core.delete_manager import DeleteManager, DeleteResult
from src.core.scanner import FileInfo, Scanner
from src.io.config import Config
from src.io.export_manager import ExportManager
from src.ui.components import CardFrame, ProgressCard, ResultCard
from src.ui.dialogs import (
    ConfirmDeleteDialog,
    ErrorDialog,
    SettingsDialog,
    choose_folder_dialog,
    choose_save_file_dialog,
)
from src.ui.theme import COLORS, FONTS, apply_theme
from src.utils.constants import APP_NAME, STRINGS
from src.utils.helpers import format_size, format_size_with_unit
from src.logger.logger import setup_logger

logger = setup_logger(__name__)


class MainWindow(ctk.CTk):
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self._lang = STRINGS[config.language]
        self._setup_window()
        self._build_ui()
        self._scanner = Scanner()
        self._analyzer = Analyzer()
        self._delete_manager = DeleteManager()
        self._export_manager = ExportManager()
        self._scan_files: List[FileInfo] = []
        self._duplicate_groups: List[DuplicateGroup] = []
        self._result_cards: List[ResultCard] = []
        self._analyzer_thread: threading.Thread = None
        self._poll_queue()

    def _setup_window(self):
        apply_theme(self.config.theme)
        self.title(f"{APP_NAME} v1.0")
        self.geometry("960x720")
        self.minsize(800, 600)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

    def _build_ui(self):
        self._build_header()
        self._build_folder_row()
        self._build_action_row()
        self._build_progress_card()
        self._build_results_area()
        self._build_bottom_bar()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=40)
        header.grid(row=0, column=0, padx=16, pady=(12, 4), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header, text=f"🔍 {APP_NAME}", font=FONTS["title"], anchor="w"
        )
        title.grid(row=0, column=0, sticky="w")

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e")

        self.settings_btn = ctk.CTkButton(
            btn_frame,
            text=self._lang["settings"],
            font=FONTS["small"],
            width=80,
            command=self._open_settings,
        )
        self.settings_btn.pack(side="left", padx=4)

        self.export_btn = ctk.CTkButton(
            btn_frame,
            text=self._lang["export"],
            font=FONTS["small"],
            width=80,
            command=self._export_results,
            state="disabled",
        )
        self.export_btn.pack(side="left", padx=4)

    def _build_folder_row(self):
        folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        folder_frame.grid(row=1, column=0, padx=16, pady=4, sticky="ew")
        folder_frame.grid_columnconfigure(0, weight=1)

        self.folder_entry = ctk.CTkEntry(
            folder_frame,
            placeholder_text=self._lang["select_folder"],
            font=FONTS["body"],
        )
        self.folder_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        if self.config.last_path:
            self.folder_entry.insert(0, self.config.last_path)

        self.browse_btn = ctk.CTkButton(
            folder_frame,
            text=self._lang["select_folder"],
            font=FONTS["small"],
            width=120,
            command=self._browse_folder,
        )
        self.browse_btn.grid(row=0, column=1)

    def _build_action_row(self):
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=2, column=0, padx=16, pady=4, sticky="ew")

        self.start_btn = ctk.CTkButton(
            action_frame,
            text=self._lang["start_scan"],
            font=FONTS["body"],
            height=36,
            command=self._start_scan,
        )
        self.start_btn.pack(side="left", padx=(0, 8))

        self.stop_btn = ctk.CTkButton(
            action_frame,
            text=self._lang["stop_scan"],
            font=FONTS["body"],
            height=36,
            command=self._stop_scan,
            state="disabled",
        )
        self.stop_btn.pack(side="left")

    def _build_progress_card(self):
        self.progress_card = ProgressCard(self)
        self.progress_card.grid(row=3, column=0, padx=16, pady=4, sticky="ew")

    def _build_results_area(self):
        self.results_container = CardFrame(self)
        self.results_container.grid(
            row=4, column=0, padx=16, pady=4, sticky="nsew"
        )
        self.results_container.grid_columnconfigure(0, weight=1)
        self.results_container.grid_rowconfigure(0, weight=1)

        self.results_scroll = ctk.CTkScrollableFrame(
            self.results_container, fg_color="transparent"
        )
        self.results_scroll.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.results_scroll.grid_columnconfigure(0, weight=1)

        self.no_results_label = ctk.CTkLabel(
            self.results_scroll,
            text=self._lang["no_duplicates"],
            font=FONTS["body"],
        )
        self.no_results_label.grid(row=0, column=0, pady=40)

    def _build_bottom_bar(self):
        bottom = ctk.CTkFrame(self, fg_color="transparent", height=36)
        bottom.grid(row=5, column=0, padx=16, pady=(4, 12), sticky="ew")
        bottom.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            bottom, text=self._lang["ready"], font=FONTS["small"], anchor="w"
        )
        self.status_label.grid(row=0, column=0, sticky="w")

        self.select_all_btn = ctk.CTkButton(
            bottom,
            text=self._lang["select_all"],
            font=FONTS["small"],
            width=140,
            command=self._select_all,
            state="disabled",
        )
        self.select_all_btn.grid(row=0, column=1, padx=4)

        self.deselect_btn = ctk.CTkButton(
            bottom,
            text=self._lang["deselect_all"],
            font=FONTS["small"],
            width=120,
            command=self._deselect_all,
            state="disabled",
        )
        self.deselect_btn.grid(row=0, column=2, padx=4)

        self.delete_btn = ctk.CTkButton(
            bottom,
            text=self._lang["delete"],
            font=FONTS["small"],
            width=140,
            command=self._delete_selected,
            state="disabled",
        )
        self.delete_btn.grid(row=0, column=3, padx=4)

    def _browse_folder(self):
        folder = choose_folder_dialog(self._lang)
        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
            self.config.last_path = folder

    def _start_scan(self):
        folder = self.folder_entry.get().strip()
        if not folder or not os.path.isdir(folder):
            ErrorDialog(self, self._lang["error"],
                        self._lang["folder_not_found"].format(folder), self._lang)
            return

        self._scan_files.clear()
        self._duplicate_groups.clear()
        self._clear_results()
        self._set_scanning_state(True)

        self.progress_card.update_progress(0)
        self.progress_card.update_stats(0, 0, "0 B", self._lang)
        self.status_label.configure(text=self._lang["scanning"])

        self._scanner.start_scan(
            folder,
            excluded_folders=self.config.excluded_folders,
            excluded_extensions=self.config.excluded_extensions,
        )

    def _stop_scan(self):
        self._scanner.stop()
        self._analyzer.stop()
        self._set_scanning_state(False)
        self.status_label.configure(text=self._lang["ready"])

    def _set_scanning_state(self, scanning: bool):
        state = "disabled" if scanning else "normal"
        self.start_btn.configure(state=state)
        self.stop_btn.configure(state="normal" if scanning else "disabled")
        self.browse_btn.configure(state=state)
        self.settings_btn.configure(state=state)

    def _poll_queue(self):
        try:
            while True:
                msg = self._scanner.queue.get_nowait()
                self._handle_scanner_message(msg)
        except Empty:
            pass

        self.after(100, self._poll_queue)

    def _handle_scanner_message(self, msg):
        msg_type = msg[0]
        if msg_type == "file_found":
            self.progress_card.update_stats(
                len(self._scan_files), 0, "0 B", self._lang
            )
        elif msg_type == "scan_complete":
            self._scan_files = msg[1]
            self.progress_card.update_stats(
                len(self._scan_files), 0, "0 B", self._lang
            )
            self._run_analysis()
        elif msg_type == "error":
            logger.error(f"Scan error: {msg[1]}")

    def _run_analysis(self):
        if not self._scan_files:
            self._set_scanning_state(False)
            self.status_label.configure(text=self._lang["scan_complete"])
            return

        self._analyzer = Analyzer()
        self._analyzer_thread = threading.Thread(target=self._analyze_worker, daemon=True)
        self._analyzer_thread.start()

    def _analyze_worker(self):
        def progress(value):
            self.after(0, lambda: self.progress_card.update_progress(value))

        groups = self._analyzer.analyze(self._scan_files, progress)
        self.after(0, lambda: self._on_analysis_complete(groups))

    def _on_analysis_complete(self, groups: List[DuplicateGroup]):
        self._analyzer_thread = None
        self._set_scanning_state(False)
        self._duplicate_groups = groups

        if not groups:
            self.status_label.configure(text=self._lang["scan_complete"])
            return

        total_wasted = sum(g.total_wasted for g in groups)
        wasted_str = format_size(total_wasted)

        self.progress_card.update_progress(1.0)
        self.progress_card.update_stats(
            len(self._scan_files), len(groups), wasted_str, self._lang
        )
        self.status_label.configure(text=self._lang["scan_complete"])

        self._display_results(groups)
        self.delete_btn.configure(state="normal")
        self.select_all_btn.configure(state="normal")
        self.deselect_btn.configure(state="normal")
        self.export_btn.configure(state="normal")

    def _display_results(self, groups: List[DuplicateGroup]):
        self._clear_results()

        for i, group in enumerate(groups, 1):
            wasted_str = format_size(group.total_wasted)
            card = ResultCard(
                self.results_scroll,
                group_index=i,
                files=group.files,
                wasted=wasted_str,
                lang=self._lang,
            )
            card.grid(row=i, column=0, padx=4, pady=4, sticky="ew")
            self._result_cards.append(card)

    def _clear_results(self):
        for widget in self.results_scroll.winfo_children():
            widget.destroy()
        self._result_cards.clear()

    def _select_all(self):
        for card in self._result_cards:
            for var, _ in card.checkboxes:
                var.set(True)

    def _deselect_all(self):
        for card in self._result_cards:
            for var, _ in card.checkboxes:
                var.set(False)

    def _delete_selected(self):
        selected = []
        for card in self._result_cards:
            selected.extend(card.get_selected())

        if not selected:
            return

        wasted = sum(f.size for f in selected)
        wasted_str = format_size(wasted)

        dialog = ConfirmDeleteDialog(self, len(selected), wasted_str, self._lang)
        if not dialog.confirmed:
            return

        result = self._delete_manager.delete_files([f.path for f in selected])
        self._handle_delete_result(result, selected)

    def _handle_delete_result(self, result: DeleteResult, selected: list):
        if result.fail_count > 0:
            ErrorDialog(
                self,
                self._lang["error"],
                self._lang["delete_error"].format(
                    "\n".join(result.failed_files)
                ),
                self._lang,
            )

        if result.success_count > 0:
            self.status_label.configure(
                text=f"Deleted {result.success_count} {self._lang['files']}"
            )
            self._refresh_after_deletion(selected)

    def _refresh_after_deletion(self, deleted_files: list):
        deleted_paths = {f.path for f in deleted_files}
        new_groups = []
        for group in self._duplicate_groups:
            remaining = [f for f in group.files if f.path not in deleted_paths]
            if len(remaining) > 1:
                new_wasted = sum(f.size for f in remaining[1:])
                new_groups.append(DuplicateGroup(
                    files=remaining, total_wasted=new_wasted
                ))
            elif len(remaining) == 1:
                pass

        self._duplicate_groups = new_groups
        self._display_results(new_groups)

        if not new_groups:
            self.delete_btn.configure(state="disabled")
            self.select_all_btn.configure(state="disabled")
            self.deselect_btn.configure(state="disabled")
            self.export_btn.configure(state="disabled")
            self.progress_card.update_stats(
                len(self._scan_files), 0, "0 B", self._lang
            )

    def _export_results(self):
        if not self._duplicate_groups:
            return

        file_path = choose_save_file_dialog(
            self._lang["export"],
            [("Text", "*.txt"), ("CSV", "*.csv")],
        )
        if not file_path:
            return

        try:
            if file_path.endswith(".csv"):
                self._export_manager.export_csv(self._duplicate_groups, file_path)
            else:
                self._export_manager.export_txt(self._duplicate_groups, file_path)
            self.status_label.configure(
                text=self._lang["export_success"].format(os.path.basename(file_path))
            )
        except Exception as e:
            ErrorDialog(
                self, self._lang["error"],
                self._lang["export_fail"].format(str(e)), self._lang
            )

    def _open_settings(self):
        SettingsDialog(self, self.config, self._lang)
        new_lang = self.config.language
        if new_lang != self._lang:
            self._lang = STRINGS[new_lang]
            self._rebuild_ui()
        apply_theme(self.config.theme)

    def _rebuild_ui(self):
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()
