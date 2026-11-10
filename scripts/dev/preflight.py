"""Refuse writes without a real studio root and sufficient backing-device space."""
import argparse
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys

GIB = 1024 ** 3


def studio_volume():
    value = os.environ.get('STUDIO_ROOT')
    if not value:
        raise ValueError('STUDIO_ROOT is not set; studio volume is not mounted')
    root = Path(value).resolve()
    if not root.is_dir():
        raise ValueError(f'Studio volume is not mounted: {root}')
    backing = root
    if sys.platform == 'darwin':
        if not os.path.ismount(root):
            raise ValueError(f'Studio volume is not mounted: {root}')
        info = plistlib.loads(subprocess.check_output(['diskutil', 'info', '-plist', str(root)]))
        if info.get('FilesystemType') != 'apfs' or not info.get('GlobalPermissionsEnabled'):
            raise ValueError('Studio volume must be APFS with ownership enabled')
        images = plistlib.loads(subprocess.check_output(['hdiutil', 'info', '-plist']))
        matched = [image for image in images.get('images', []) if any(entity.get('mount-point') == str(root) for entity in image.get('system-entities', []))]
        if len(matched) != 1:
            raise ValueError('Cannot resolve studio image backing device')
        backing = Path(matched[0]['image-path']).resolve().parent
        host = plistlib.loads(subprocess.check_output(['diskutil', 'info', '-plist', str(backing)]))
        physical_buses = {'USB', 'Thunderbolt', 'PCI-Express', 'FireWire', 'SATA'}
        if host.get('Internal') is not False or host.get('BusProtocol') not in physical_buses:
            raise ValueError('Studio image must be hosted on a verified external physical volume (unknown buses and nested images are not supported)')
    return root, backing


def check(estimate_bytes=0):
    if estimate_bytes < 0:
        raise ValueError('Write estimate must be nonnegative')
    root, backing = studio_volume()
    # Reserve a conservative band allowance in addition to the ten-GiB free margin.
    free = min(shutil.disk_usage(root).free, shutil.disk_usage(backing).free) - 64 * 1024 ** 2
    if free - estimate_bytes < 10 * GIB:
        raise ValueError(f'insufficient studio space: {free} bytes available, {estimate_bytes} needed, {10 * GIB} margin')
    if sys.platform == 'darwin' and shutil.disk_usage('/System/Volumes/Data').free < 2 * GIB:
        raise ValueError('Internal disk below two-GiB safety floor; no heavy operation allowed')
    return {'root': str(root), 'backing': str(backing), 'effective_free_bytes': free, 'estimate_bytes': estimate_bytes, 'margin_bytes': 10 * GIB}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--estimate-gib', type=int, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(check(args.estimate_gib * GIB), indent=2))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'{error}\n')
