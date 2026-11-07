"""Validate a fresh tracked-file copy; ignored local fixtures cannot mask failures."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root=Path(__file__).resolve().parents[2]
files=[os.fsdecode(name) for name in subprocess.check_output(['git','-C',str(root),'ls-files','-z']).split(b'\0') if name]
with tempfile.TemporaryDirectory(prefix='tracked-contracts-') as temporary:
    target=Path(temporary)
    for name in files:
        if name and (root/name).is_file():
            destination=target/name;destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(root/name,destination)
    for command in [['scripts/spec/validate.py'],['scripts/registry/sync.py','--check'],['scripts/spec/tickets.py','--check']]:
        subprocess.run([sys.executable,*command],cwd=target,check=True)
