"""Check actual installed control-runtime and web production dependency closures."""
import argparse
import hashlib
from importlib import metadata
import json
from pathlib import Path
import shutil
import subprocess
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from check import license_allowed, DENIED

CLASSIFIERS = {
    'License :: OSI Approved :: MIT License': 'MIT',
    'License :: OSI Approved :: Apache Software License': 'Apache-2.0',
    'License :: OSI Approved :: Python Software Foundation License': 'PSF-2.0',
    'License :: OSI Approved :: ISC License (ISCL)': 'ISC',
}


def control_inventory():
    pending=[(requirement, {''}) for requirement in metadata.requires('studio-control') or []]
    result={};expanded={}
    while pending:
        value, parent_extras = pending.pop()
        requirement=Requirement(value)
        if requirement.marker and not any(requirement.marker.evaluate({'extra':extra}) for extra in parent_extras):
            continue
        distribution=metadata.distribution(requirement.name)
        name=canonicalize_name(distribution.metadata['Name'])
        if distribution.version not in requirement.specifier:
            raise ValueError('Installed version violates the runtime requirement')
        extras=set(requirement.extras)|{''}
        if name in expanded and extras <= expanded[name]:
            continue
        expanded.setdefault(name,set()).update(extras)
        data=distribution.metadata
        classifiers=data.get_all('Classifier',[])
        license=data.get('License-Expression')
        legacy=data.get('License','')
        license_classifiers=[item for item in classifiers if item.startswith('License ::')]
        if DENIED.search(legacy) or any(DENIED.search(item) for item in license_classifiers):
            license='DISALLOWED'
        elif not license:
            classified=[CLASSIFIERS.get(item,'UNKNOWN') for item in license_classifiers]
            if classified:
                license=classified[0] if len(set(classified))==1 else 'UNKNOWN'
                if legacy and license_allowed(legacy) and legacy!=license:
                    license='UNKNOWN'
            else:
                license=legacy or 'UNKNOWN'
        result[name]={'surface':'control','name':name,'version':distribution.version,'license':license}
        pending.extend((child,expanded[name].copy()) for child in distribution.requires or [])
    return list(result.values())


def web_inventory(root):
    bundle=root/'apps/web/dist'
    inventory=json.loads((bundle/'license-inventory.json').read_text())
    if inventory['generatedModules']:
        raise ValueError('Unverified generated bundler module')
    chunks=inventory['chunks']
    if not chunks: raise ValueError('Bundle contains no verified chunks')
    for filename,digest in chunks.items():
        path=(bundle/filename).resolve()
        if not path.is_relative_to(bundle.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise ValueError('Bundle inventory does not match emitted bytes')
    if set(path.relative_to(bundle).as_posix() for path in bundle.rglob('*.js')) != set(chunks):
        raise ValueError('Uninventoried JavaScript in built bundle')
    return [dict(item,surface='web') for item in inventory['packages']]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python-only',action='store_true',help='Control environment check without a web build')
    args=parser.parse_args()
    try:
        inventory=control_inventory()
        if not args.python_only: inventory.extend(web_inventory(Path(__file__).resolve().parents[2]))
        print(json.dumps(inventory,indent=2))
        bad=[item for item in inventory if not license_allowed(item['license'])]
        for item in bad: print(f"license: {item['surface']} dependency {item['name']} is disallowed or unverified")
        return bool(bad)
    except Exception as error:
        print(f'license: inventory could not be verified ({type(error).__name__})')
        return 1


if __name__=='__main__': raise SystemExit(main())
