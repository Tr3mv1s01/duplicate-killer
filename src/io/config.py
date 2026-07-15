import json
import os

from src.utils.constants import DEFAULT_SETTINGS, SETTINGS_FILE


class Config:
    def __init__(self):
        self._settings = dict(DEFAULT_SETTINGS)
        self._config_dir = self._get_config_dir()
        self._config_path = os.path.join(self._config_dir, SETTINGS_FILE)
        self._ensure_config_dir()
        self.load()

    def _get_config_dir(self) -> str:
        if os.name == "nt":
            base = os.environ.get("APPDATA", os.path.expanduser("~"))
        else:
            base = os.path.expanduser("~/.config")
        return os.path.join(base, "DuplicateKiller")

    def _ensure_config_dir(self):
        os.makedirs(self._config_dir, exist_ok=True)

    def load(self):
        if not os.path.exists(self._config_path):
            self.save()
            return
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for key in DEFAULT_SETTINGS:
                if key in data:
                    self._settings[key] = data[key]
        except (json.JSONDecodeError, OSError):
            pass

    def save(self):
        try:
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def get(self, key: str):
        return self._settings.get(key, DEFAULT_SETTINGS.get(key))

    def set(self, key: str, value):
        self._settings[key] = value
        self.save()

    @property
    def theme(self) -> str:
        return self.get("theme")

    @theme.setter
    def theme(self, value: str):
        self.set("theme", value)

    @property
    def language(self) -> str:
        return self.get("language")

    @language.setter
    def language(self, value: str):
        self.set("language", value)

    @property
    def excluded_folders(self) -> list:
        return list(self.get("excluded_folders"))

    @excluded_folders.setter
    def excluded_folders(self, value: list):
        self.set("excluded_folders", value)

    @property
    def excluded_extensions(self) -> list:
        return list(self.get("excluded_extensions"))

    @excluded_extensions.setter
    def excluded_extensions(self, value: list):
        self.set("excluded_extensions", value)

    @property
    def last_path(self) -> str:
        return self.get("last_path")

    @last_path.setter
    def last_path(self, value: str):
        self.set("last_path", value)
