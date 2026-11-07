"""Repository policy checks. Diagnostics name files and rules, never secret values."""
import argparse
import json
from pathlib import Path
import re
import subprocess

EMAIL = re.compile(r'[A-Za-z0-9.!#$%&\x27*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
SECRET = re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,}|hf_[A-Za-z0-9]{30,}|AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|(?:api_key|api_token|secret_key)\s*[=:]\s*["\x27][A-Za-z0-9_/-]{24,})', re.I)
ALLOWED = {'MIT', 'BSD-2-Clause', 'BSD-3-Clause', 'Apache-2.0', 'ISC', '0BSD', 'PSF-2.0', 'Python-2.0', 'CC0-1.0', 'OFL-1.1'}
DENIED = re.compile(r'(?:L?GPL|AGPL|CC-BY-NC|CC-BY-SA|SSPL|BUSL)', re.I)
WEIGHTS = {'.safetensors','.ckpt','.pt','.pth','.onnx','.gguf','.bin','.h5','.hdf5'}
AUDIO = {'.wav','.flac','.mp3','.aif','.aiff','.ogg','.opus','.m4a','.aac','.aifc'}


def license_allowed(value):
    # Deliberately fail closed on unsupported SPDX syntax and all copyleft options.
    if not isinstance(value,str) or DENIED.search(value):
        return False
    parts = re.split(r'\s+(?:OR|AND)\s+',value.strip('() '))
    return bool(parts) and all(part.strip('() ') in ALLOWED for part in parts)


def contact_errors(path,text,allowed):
    problems=[]
    if re.search(r'mailto\s*:[^\s\x60<>]*@',text,re.I): problems.append('contact: mail link')
    fenced=False
    for line in text.splitlines():
        if line.lstrip().startswith(('```','~~~')): fenced=not fenced
        for match in EMAIL.finditer(line):
            # Backticks delimit Markdown rather than belonging to an address.
            address=match.group().strip('`')
            if address!=allowed:
                problems.append('contact: unapproved address')
            elif path.suffix=='.md' and not fenced:
                before=line[:match.start()]
                if (before.count('`') + (1 if match.group().startswith('`') else 0)) % 2 != 1:
                    problems.append('contact: Markdown address must be code formatted')
    return problems


def scan_file(root,relative,product,contact):
    path=root/relative; errors=[]
    if not path.is_file(): return errors
    if path.suffix.lower() in WEIGHTS or path.stat().st_size>=50*1024**2: errors.append('weights: prohibited extension or large tracked file')
    if path.suffix.lower() in AUDIO: errors.append('audio: audio must not be committed')
    if path.stat().st_size>50*1024**2: return errors
    try: text=path.read_text(encoding='utf-8')
    except UnicodeDecodeError: return errors
    if SECRET.search(text): errors.append('secret: credential-shaped content')
    if not relative.startswith('docs/research/sources/'):
        errors.extend(contact_errors(path,text,contact))
    if path.name in {'package.json','pyproject.toml'}:
        if re.search(r'\bauthors?\b',text,re.I) and EMAIL.search(text): errors.append('manifest: author email forbidden')
    is_code=path.suffix in {'.py','.ts','.tsx','.js','.mjs','.sh','.toml','.yaml','.yml'} or path.name=='package.json'
    if is_code and not relative.startswith(('docs/','contracts/','ops/mission/')):
        # Legacy design filenames are documentation references, not runtime identifiers.
        code=text
        for document in (root/'docs').rglob('*.md'):
            code=code.replace(document.name, '')
        if re.search(re.escape(product),code,re.I): errors.append('product-name: literal product name outside contract')
    if product.lower() in relative.lower() and not relative.startswith(('docs/','contracts/','ops/mission/')):
        errors.append('product-name: product name in path')
    if path.name=='license-inventory.json':
        for entry in json.loads(text):
            if not license_allowed(entry.get('license')): errors.append('license: disallowed or unknown inventory license')
    return errors


def commit_errors(root,base):
    args=['git','-C',str(root),'-c','i18n.logOutputEncoding=UTF-8','log','--format=%H%x00%ae%x00%ce%x00%B%x00', f'{base}..HEAD' if base else '-1']
    raw=subprocess.check_output(args,encoding='utf-8',errors='surrogateescape')
    allowed=re.compile(r'^(?:\d+\+)?(?:Navigata1|web-flow)@users\.noreply\.github\.com$|^noreply@github\.com$')
    coauthor=re.compile(r'^noreply@anthropic\.com$')
    errors=[]
    parts=raw.split('\0')
    for i in range(0,len(parts)-3,4):
        sha,author,committer,body=parts[i:i+4]
        if not allowed.fullmatch(author) or not allowed.fullmatch(committer): errors.append((sha.strip()[:12],'contact: commit identity must use noreply'))
        for line in body.splitlines():
            for match in EMAIL.finditer(line):
                email=match.group().strip('`')
                if not (line.lower().startswith('co-authored-by:') and coauthor.fullmatch(email)):
                    errors.append((sha.strip()[:12],'contact: address in commit message'))
    return errors


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    parser.add_argument('--base',help='Commit whose descendants are checked; PR base SHA in CI')
    parser.add_argument('--files-only',action='store_true',help='Local/test fixture scan; CI also checks commits')
    parser.add_argument('--bundle',action='store_true',help='Require and scan the actual built web bundle')
    args=parser.parse_args();root=args.root.resolve()
    product=json.loads((root/'contracts/product.json').read_text(encoding='utf-8'))
    files=set(subprocess.check_output(['git','-C',str(root),'ls-files','-z'],encoding='utf-8',errors='surrogateescape').split('\0'))-{''}
    errors=[]
    for relative in sorted(files):
        errors.extend((relative,error) for error in scan_file(root,relative,product['productName'],product['publicContactText']))
    if args.bundle:
        bundle=root/'apps/web/dist'
        if not bundle.is_dir(): errors.append(('apps/web/dist','secret: built bundle is missing'))
        else:
            for path in bundle.rglob('*'):
                if path.is_file():
                    try:text=path.read_text(encoding='utf-8')
                    except UnicodeDecodeError:continue
                    if SECRET.search(text): errors.append((str(path.relative_to(root)),'secret: credential-shaped bundle content'))
    if args.base:
        diff=subprocess.check_output(['git','-C',str(root),'diff','--no-ext-diff',args.base,'--'],encoding='utf-8',errors='surrogateescape')
        if SECRET.search(diff): errors.append(('PR diff','secret: credential-shaped content'))
    if not args.files_only: errors.extend(commit_errors(root,args.base))
    for path,error in errors:
        # Paths may contain Unicode or undecodable filesystem bytes; diagnostics must also work on ASCII consoles.
        print(f'{path}: {error}'.encode('ascii',errors='backslashreplace').decode('ascii'))
    print(f'Policy scan: {len(files)} tracked files; {len(errors)} violations')
    return bool(errors)


if __name__=='__main__': raise SystemExit(main())
