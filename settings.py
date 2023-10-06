import json


class RepositorySettingsManager:
    def __init__(self, repo: "Repository"):
        self._repo = repo

    def save(self):
        file = self._repo.local_path / "ziprepo.json"
        with open(file, "w", encoding="utf-8") as fobj:
            json.dump(self._repo.config, fobj, indent=4)

    def load(self):
        config = self._repo.config
        file = self._repo.local_path / "ziprepo.json"
        if file.exists():
            with open(file, "r", encoding="utf-8") as fobj:
                loaded_config = json.load(fobj)
        else:
            loaded_config = {}
        config.update(loaded_config)
        config.setdefault("type", "repo")
        config.setdefault("storages", {})
        config.setdefault("exclude", [])
        config.setdefault("version", 0)
        if not file.exists():
            self.save()


class StorageSettingsManager:
    def __init__(self, storage: "ExternalStorage"):
        self._storage = storage

    def save(self):
        file = self._repo.path / "ziprepo.json"
        with open(file, "w", encoding="utf-8") as fobj:
            json.dump(self._repo.config, fobj)

    def load(self):
        file = self._repo.path / "ziprepo.json"
        config = self._repo.config
        if file.exists():
            with open(file, "r", encoding="utf-8") as fobj:
                loaded_config = json.load(file)
        else:
            loaded_config = {}
        config.update(loaded_config)
        config.setdefault("type", "storage")
        if not file.exists():
            self.save()
