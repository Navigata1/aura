"""Synthetic OS boundary for CI. This helper never ships in a runtime package."""
import os
import shutil
import subprocess
import sys
from pathlib import Path


def native_bash():
    """Use Git for Windows Bash, never the unrelated WSL bash launcher on PATH."""
    if os.name != 'nt':
        bash = shutil.which('bash')
        if not bash:
            raise RuntimeError('Bash is required for the shell environment contract')
        return bash
    git = shutil.which('git')
    if not git:
        raise RuntimeError('Git for Windows is required for the shell environment contract')
    exec_path = Path(subprocess.check_output([git, '--exec-path'], text=True).strip())
    for parent in (exec_path, *exec_path.parents):
        candidate = parent / 'bin/bash.exe'
        if candidate.is_file():
            return str(candidate)
    raise RuntimeError('Git for Windows Bash was not found beside its git executable')


def managed_python_shell_path():
    # Git Bash accepts drive-qualified forward slashes; backslashes are shell syntax.
    return Path(sys.executable).as_posix()


def boundary_environment(root):
    """A disposable root; fake only OS mount metadata, not studio implementation."""
    root=Path(root)
    shim=root/'os-boundary';shim.mkdir()
    (shim/'sitecustomize.py').write_text('''import os, plistlib, subprocess
original_mount=os.path.ismount
original_output=subprocess.check_output
root=os.environ["STUDIO_TEST_MOUNT"]
os.path.ismount=lambda path: str(path)==root or original_mount(path)
def output(args,*a,**kw):
    if args[:3]==["diskutil","info","-plist"] and args[3]==root:
        return plistlib.dumps({"FilesystemType":"apfs","GlobalPermissionsEnabled":True,"MountPoint":root})
    if args[:3]==["diskutil","info","-plist"] and args[3]==root+"/host":
        return plistlib.dumps({"Internal":False,"BusProtocol":"USB"})
    if args==["hdiutil","info","-plist"]:
        return plistlib.dumps({"images":[{"image-path":root+"/host/test.sparsebundle","system-entities":[{"mount-point":root}]}]})
    return original_output(args,*a,**kw)
subprocess.check_output=output
''')
    (root/'host').mkdir()
    return {**os.environ,'STUDIO_ROOT':str(root),'STUDIO_TEST_MOUNT':str(root),'PYTHONPATH':str(shim),'STUDIO_PYTHON':managed_python_shell_path()}
