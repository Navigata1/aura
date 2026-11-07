"""Foundation gate: contracts, package tests, builds, policy and runtime licenses."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

root=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--base',help='Base commit for PR diff and commit-policy checks')
parser.add_argument('--files-only',action='store_true',help='Preparation before a commit; never used in CI')
args=parser.parse_args()

def run(command):
    print('+ '+' '.join(command),flush=True)
    subprocess.run(command,cwd=root,check=True)

# Local builds use the strict actual-volume adapter. Hosted CI is a disposable test host.
if not (os.environ.get('GITHUB_ACTIONS')=='true' and os.environ.get('RUNNER_ENVIRONMENT')=='github-hosted'):
    if not root.is_relative_to(Path(os.environ.get('STUDIO_ROOT', '/not-mounted')).resolve()):
        raise SystemExit('Local builds require a worktree on STUDIO_ROOT')
    run([sys.executable,'scripts/dev/preflight.py','--estimate-gib','1'])
expected_node=(root/'.node-version').read_text().strip()
actual_node=subprocess.check_output([shutil.which('node'),'--version'],text=True).strip().removeprefix('v')
if actual_node!=expected_node:raise SystemExit('Use the pinned Node version from .node-version')
run([sys.executable,'scripts/ci/clean_contracts.py'])
run([sys.executable,'-m','pytest','-q'])
pnpm=shutil.which('pnpm')
if not pnpm:raise SystemExit('pnpm missing')
run([pnpm,'test'])
run([shutil.which('node'),'--test','scripts/ci/tests/bundle-licenses.test.mjs'])
run([pnpm,'build'])
command=[sys.executable,'scripts/ci/check.py','--bundle']
if args.base:command+=['--base',args.base]
if args.files_only:command+=['--files-only']
run(command)
run([sys.executable,'scripts/ci/licenses.py'])
print('Foundation gate passed. Synthetic/software evidence only; no playback or music-quality claim.')
