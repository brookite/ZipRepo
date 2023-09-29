import json


class RepositorySettingsManager:
    def __init__(self, repo: "Repository"):
        self._repo = repo

    def save(self):
        file = self._repo.local_path / "ziprepo.json"
        with open(file, "w", encoding="utf-8") as fobj:
            json.dump(self._repo.config, file)

    def load(self):
        config = self._repo.config
        file = self._repo.local_path / "ziprepo.json"
        with open(file, "r", encoding="utf-8") as fobj:
            loaded_config = json.load(file)
        config.update(loaded_config)
        config.setdefault("type", "repo")
        config.setdefault("storages", {})
        config.setdefault("version", 0)


class StorageSettingsManager:
    def __init__(self, storage: "ExternalStorage"):
        self._storage = storage

    def save(self):
        file = self._repo.path / "ziprepo.json"
        with open(file, "w", encoding="utf-8") as fobj:
            json.dump(self._repo.config, file)

    def load(self):
        file = self._repo.path / "ziprepo.json"
        config = self._repo.config
        with open(file, "r", encoding="utf-8") as fobj:
            loaded_config = json.load(file)
        config.update(loaded_config)
        config.setdefault("type", "repo")