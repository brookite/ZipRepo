from pathlib import Path
from storage import ExternalStorage
from repository import Repository

class ZipManager:
    def pack(self, repo: Repository):
        pass

    def unpack(self, path: Path):
        pass

    def move(self, zip_file: Path, storage: ExternalStorage):
        pass


class PushManager:
    pass


class PullManager:
    pass
