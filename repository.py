from pathlib import Path
from settings import RepositorySettingsManager


class Repository:
    def __init__(self, local_path: Path):
        self._local_path = local_path
        self._config = {}
        self._initialize()

    def _initialize(self):
        RepositorySettingsManager(self).load()

    @property
    def local_path(self) -> Path:
        return self._local_path

    @property
    def name(self):
        return self._local_path.name

    @property
    def version(self):
        return self._config["version"]

    @property
    def config(self):
        return self._config

    def update_version(self) -> int:
        self.config["version"] += 1
        return self._config["version"]

    def add_external_storage(self, name: str, storage: "ExternalStorage"):
        self._config["storages"]["name"] = storage.path
