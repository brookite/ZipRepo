from managers import ZipManager
from repository import Repository
from pathlib import Path

rep = Repository(Path.cwd())
for item in rep.local_path.iterdir():
    print(item.relative_to(rep.local_path).match("*.py"))
ZipManager.pack(rep, Path.cwd())
