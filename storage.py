import os
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

    @property
    def config(self):
        return self._config

    def find_repository(self, name):
        files = []
        for file in os.listdir(self.path):
            file = self.path / Path(file)
            if file.is_file() and file.match("*_v*.ziprepo"):
                repo_name = "_".join(str(file.name).split("_")[-2::-1][::-1])
                version = int(file.name.split("_v")[-1].replace(".ziprepo", ""))
                if repo_name == name:
                    files.append((version, file))
        files.sort(key=lambda info: info[0])
        if len(files):
            return files[-1][1]
