from pathlib import Path
from settings import SettingsManager


class Repository:
    def __init__(self, local_path: Path):
        self._local_path = local_path
        self._config = {}
        self._initialize()

    def _initialize(self):
        SettingsManager(self).load()

    @property
    def local_path(self) -> Path:
        return self._local_path

    @property
    def name(self):
        pass

    @property
    def config(self):
        return self._config

    def update_version(self) -> int:
        self.config["version"] += 1
        return self._config["version"]

    def add_external_storage(self, storage):
        pass
