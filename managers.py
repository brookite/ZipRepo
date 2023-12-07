import json
import zipfile
from pathlib import Path
from typing import Optional

from settings import RepositorySettingsManager, GlobalSettingsManager
from storage import ExternalStorage
from repository import Repository
import os
from shutil import move, rmtree

DEFAULT_EXCLUDE = [".git/"]


class PushProcessError(Exception):
    pass


class PullProcessError(Exception):
    pass


class ZipManager:
    @staticmethod
    def pack(repo: Repository, zip_path: Path) -> Path:
        zipname = f"{repo.name}_v{repo.version}.ziprepo"
        filepath = zip_path / zipname
        excluded = DEFAULT_EXCLUDE + repo.config["exclude"]
        with zipfile.ZipFile(
            filepath,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as zip:
            ignored_root = None
            for root, dirs, files in os.walk(repo.local_path):
                root = Path(root)

                if ignored_root and root == ignored_root:
                    continue
                else:
                    ignored_root = None

                continue_flag = False
                for exc in excluded:
                    if (
                        Path(exc) in root.relative_to(repo.local_path).parents
                        or root.relative_to(repo.local_path).match(exc)
                        or root.relative_to(repo.local_path) == Path(exc)
                    ):
                        ignored_root = root
                        continue_flag = True
                        break

                if continue_flag:
                    continue

                for dir in dirs:
                    continue_flag = False
                    path = root / dir
                    local_excluded = []
                    for exc in excluded:
                        if (
                            Path(exc) == Path(dir)
                            or Path(exc) in path.relative_to(repo.local_path).parents
                            or path.relative_to(repo.local_path).match(exc)
                            or path.relative_to(repo.local_path) == Path(exc)
                        ):
                            continue_flag = True
                            local_excluded.append(path)
                    excluded.extend(local_excluded)
                    if not continue_flag:
                        zip.mkdir(str(path.relative_to(repo.local_path)))
                for file in files:
                    path = root / file
                    if path.name == zipname:
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
