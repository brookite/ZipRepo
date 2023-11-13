import abc
import json
import os.path
import uuid
from collections import namedtuple
from pathlib import Path
from typing import Any


class AbstractSettingsManager(abc.ABC):
    _source: Any

    def save(self):
        file = self._source.path / "ziprepo.json"
        with open(file, "w", encoding="utf-8") as fobj:
            json.dump(self._source.config, fobj)

    def load(self):
        file = self._source.path / "ziprepo.json"
        config = self._source.config
        if file.exists():
            with open(file, "r", encoding="utf-8") as fobj:
                loaded_config = json.load(fobj)
        else:
            loaded_config = {}
        config.update(loaded_config)


class GlobalSettingsManager(AbstractSettingsManager):
    LocalSettings = namedtuple("LocalSettings", ["config", "path"])

    def __init__(self):
        self._source = GlobalSettingsManager.LocalSettings(
            {}, Path(os.path.expanduser("~"))
        )
        self.load()

    def add_storage(self, name: str, path: str):
        self._source.config["aliases"][name] = path

    def remove_storage(self, name: str):
        self._source.config["aliases"].pop(name)

    def load(self):
        super().load()
        config = self._source.config
        config.setdefault("type", "global")
        config.setdefault("aliases", {})

    def get_alias(self, storage_name):
        return self._source.config.get("aliases", {}).get(storage_name)


class RepositorySettingsManager(AbstractSettingsManager):
    def __init__(self, repo: "Repository"):
        self._source = repo

    def load(self):
        super().load()
        config = self._source.config
        config.setdefault("type", "repo")
        config.setdefault("id", str(uuid.uuid4()))
        config.setdefault("storages", {})
        config.setdefault("exclude", [])
        config.setdefault("version", 0)
        self.save()


class StorageSettingsManager(AbstractSettingsManager):
    def __init__(self, storage: "ExternalStorage"):
        self._source = storage

    def load(self):
        super().load()
        config = self._source.config
        config.setdefault("id", str(uuid.uuid4()))
        config.setdefault("type", "storage")
        self.save()
