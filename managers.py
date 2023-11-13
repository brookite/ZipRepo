import json
import zipfile
from pathlib import Path
from typing import Optional

from settings import RepositorySettingsManager, GlobalSettingsManager
from storage import ExternalStorage
from repository import Repository
import os
from shutil import move, rmtree

DEFAULT_EXCLUDE = [".git/*", ".git"]


class PushProcessError(Exception):
    pass


class PullProcessError(Exception):
    pass


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
            skip_dirs = []
            for root, dirs, files in os.walk(repo.local_path):
                root = Path(root)
                for dir in dirs:
                    skip_path = False
                    path = root / dir
                    for exc in DEFAULT_EXCLUDE + repo.config["exclude"]:
                        if path.relative_to(repo.local_path).match(exc):
                            skip_path = True
                            skip_dirs.append(path)
                    for skip_dir in skip_dirs:
                        if skip_dir in path.parents:
                            skip_path = True
                    if not skip_path:
                        zip.mkdir(str(path.relative_to(repo.local_path)))
                for file in files:
                    skip_path = False
                    path = root / file
                    if path.name == zipname:
                        skip_path = True
                    for skip_dir in skip_dirs:
                        if skip_dir in path.parents:
                            skip_path = True
                    for exc in DEFAULT_EXCLUDE + repo.config["exclude"]:
                        if path.relative_to(repo.local_path).match(exc):
                            skip_path = True
                    if not skip_path:
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
        RepositorySettingsManager(repo).save()
        if storage_name:
            storage_path = repo.config["storages"].get(storage_name)
            if not storage_path:
                settings = GlobalSettingsManager()
                if not (storage_path := settings.get_alias(storage_name)):
                    raise PushProcessError("Storage wasn't found")
            storage = ExternalStorage(Path(storage_path))
            file = ZipManager.pack(repo, repo.local_path)
            if ff := storage.find_repository(repo.name):
                version = PullManager.extract_version(ff)
                if repo.version < version:
                    raise PushProcessError(
                        f"Detected newest version in storage {storage_path}. "
                        "Please, save changes and pull before pushing"
                    )
            ZipManager.move(file, storage)
        else:
            for storage_path in repo.config["storages"].values():
                storage = ExternalStorage(Path(storage_path))
                file = ZipManager.pack(repo, repo.local_path)
                if ff := storage.find_repository(repo.name):
                    version = PullManager.extract_version(ff)
                    if repo.version < version:
                        raise PushProcessError(
                            f"Detected newest version in storage {storage_path}. "
                            "Please, save changes and pull before pushing"
                        )
                ZipManager.move(file, storage)


class PullManager:
    @staticmethod
    def extract_version(zip_file: Path) -> int:
        file = ZipManager.view_file(zip_file, "ziprepo.json").decode("utf-8")
        jsonfile = json.loads(file)
        return jsonfile.get("version", 0)

    @staticmethod
    def pull(repo: Repository, storage_name: str):
        storage_path = repo.config["storages"].get(storage_name)
        if not storage_path:
            settings = GlobalSettingsManager()
            if not (storage_path := settings.get_alias(storage_name)):
                raise PushProcessError("Storage wasn't found")
        storage = ExternalStorage(Path(storage_path))
        if file := storage.find_repository(repo.name):
            version = PullManager.extract_version(file)
            if version > repo.version:
                rmtree(repo.local_path, ignore_errors=True)
                if not repo.local_path.exists():
                    os.mkdir(repo.local_path)
                ZipManager.unpack(file, repo.local_path)
