"""Synthetic OS boundary for CI. This helper never ships in a runtime package."""
import os
import sys
from pathlib import Path


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
    return {**os.environ,'STUDIO_ROOT':str(root),'STUDIO_TEST_MOUNT':str(root),'PYTHONPATH':str(shim),'STUDIO_PYTHON':sys.executable}
