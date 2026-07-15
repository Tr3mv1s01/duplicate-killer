import customtkinter as ctk

from src.io.config import Config
from src.logger.logger import setup_logger
from src.ui.main_window import MainWindow

logger = setup_logger(__name__)


class App:
    def __init__(self):
        self.config = Config()
        self._setup_ctk()
        self.window = MainWindow(self.config)

    @staticmethod
    def _setup_ctk():
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

    def run(self):
        logger.info("Application started")
        try:
            self.window.mainloop()
        except Exception as e:
            logger.exception(f"Application crashed: {e}")
            raise
