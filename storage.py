from pathlib import Path
from settings import StorageSettingsManager

class ExternalStorage:
    def __init__(self, path: Path):
        self._path = path
        self._config = {}
        self._initialize()

    def _initialize(self):
        StorageSettingsManager(self).load()

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._path.name
