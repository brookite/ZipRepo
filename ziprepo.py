import os
import sys

from managers import ZipManager, PushManager, PullManager
from repository import Repository
from pathlib import Path

from settings import RepositorySettingsManager, GlobalSettingsManager
from storage import ExternalStorage


def init():
    Repository(Path.cwd())


def ext_init():
    ExternalStorage(Path.cwd())


def ext_add(name, path):
    repository = Repository(Path.cwd())
    if os.path.exists(path):
        if os.path.exists(os.path.join(path, "ziprepo.json")):
            repository.config["storages"][name] = path
            RepositorySettingsManager(repository).save()
        else:
            print("It's not storage path", file=sys.stderr)
    else:
        print("Storage doesn't exist", file=sys.stderr)


def ext_remove(name):
    repository = Repository(Path.cwd())
    repository.config["storages"].pop(name)
    RepositorySettingsManager(repository).save()


def ext_clone(source, repo_name):
    cur_path = Path.cwd()
    storage = ExternalStorage(Path(source))
    if zip_path := storage.find_repository(repo_name):
        ZipManager.unpack(zip_path, cur_path / repo_name)
    else:
        print("Repository doesn't exist in specified storage", file=sys.stderr)


def push(storage_name):
    repository = Repository(Path.cwd())
    storage_name = None if storage_name.lower() == "all" else storage_name
    PushManager.push(repository, storage_name)


def pull(storage_name):
    repository = Repository(Path.cwd())
    PullManager.pull(repository, storage_name)


def add_global_storage_alias(name, path):
    settings = GlobalSettingsManager()
    settings.load()
    settings.add_storage(name, path)
    settings.save()


def remove_global_storage_alias(name):
    settings = GlobalSettingsManager()
    settings.load()
    settings.remove_storage(name)
    settings.save()


def help():
    pass


COMMANDS = {
    "init": init,
    "ext": {"add": ext_add, "remove": ext_remove, "clone": ext_clone, "init": ext_init},
    "global": {
        "storage": {
            "add": add_global_storage_alias,
            "remove": remove_global_storage_alias,
        }
    },
    "push": push,
    "pull": pull,
    "help": help,
    "--help": help,
}


def main():
    arguments = sys.argv[1:]
    if len(arguments) == 0:
        print("Input valid command sequence to ziprepo", file=sys.stderr)
    else:
        i = 0
        target = COMMANDS[arguments[i]]
        while not callable(target):
            i += 1
            if i == len(arguments):
                print("Invalid command sequence", file=sys.stderr)
                return
            target = target[arguments[i]]
        args = sys.argv[i + 2 :]
        target(*args)


if __name__ == "__main__":
    main()
