import json
import zipfile
from pathlib import Path
from typing import Optional

from storage import ExternalStorage
from repository import Repository
import os
from shutil import move, rmtree

DEFAULT_EXCLUDE = [".git"]


class ZipManager:
    @staticmethod
    def pack(repo: Repository, zip_path: Path) -> Path:
        zipname = f"{repo.name}_v{repo.version}.ziprepo"
        filepath = zip_path / zipname
        with zipfile.ZipFile(
            filepath,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as zip:
            for root, dirs, files in os.walk(repo.local_path):
                root = Path(root)
                for dir in dirs:
                    path = (root / dir).relative_to(repo.local_path)
                    if path.name in DEFAULT_EXCLUDE:
                        continue
                    for exc in repo.config["exclude"]:
                        if path.match(exc):
                            continue
                    zip.mkdir(str(path))
                for file in files:
                    path = root / file
                    if path.name in DEFAULT_EXCLUDE:
                        continue
                    for exc in repo.config["exclude"]:
                        if path.relative_to(repo.local_path).match(exc):
                            continue
                    zip.write(path, path.relative_to(repo.local_path))
        return filepath

    @staticmethod
    def unpack(zip_path: Path, unpack_path: Path) -> None:
        with zipfile.ZipFile(
            zip_path,
            "r",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as zip:
            zip.extractall(unpack_path)

    @staticmethod
    def move(zip_file: Path, storage: ExternalStorage):
        return move(zip_file, storage.path)

    @staticmethod
    def view_file(zip_file: Path, internal_path: str):
        with zipfile.ZipFile(
            zip_file,
            "r",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as zip:
            return zip.read(internal_path)


class PushManager:
    @staticmethod
    def push(repo: Repository, storage_name: Optional[str] = None):
        repo.update_version()
        if storage_name:
            storage_path = repo.config["storages"].get(storage_name)
            storage = ExternalStorage(Path(storage_path))
            file = ZipManager.pack(repo, repo.local_path)
            ZipManager.move(file, storage)
        else:
            for storage_path in repo.config["storages"].values():
                storage = ExternalStorage(Path(storage_path))
                file = ZipManager.pack(repo, repo.local_path)
                ZipManager.move(file, storage)


class PullManager:
    @staticmethod
    def extract_version(zip_file: Path) -> int:
        file = ZipManager.view_file(zip_file, "ziprepo.json").decode("utf-8")
        jsonfile = json.loads(file)
        return jsonfile.get("version", 0)

    @staticmethod
    def _pull_storage(repo: Repository, storage_name: str):
        storage_path = repo.config["storages"].get(storage_name)
        for file in os.listdir(storage_path):
            file = Path(file)
            if file.is_file() and file.match("*_v*.ziprepo"):
                repo_name = str(file.name).split("_")[0]
                if repo_name == repo.name:
                    version = PullManager.extract_version(file)
                    if version > repo.version:
                        rmtree(repo.local_path)
                        os.mkdir(repo.local_path)
                        ZipManager.unpack(file, repo.local_path)

    @staticmethod
    def pull(repo: Repository, storage_name: str):
        if storage_name:
            PullManager._pull_storage(repo, storage_name)
        else:
            for storage in repo.config["storages"]:
                PullManager._pull_storage(repo, storage)
