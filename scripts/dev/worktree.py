"""Create one ticket worktree on the studio volume from its external bare clone."""
import argparse
import os
from pathlib import Path
import re
import subprocess
from preflight import check


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ticket', help='Ticket number and slug, for example 01-foundation')
    args = parser.parse_args()
    if not re.fullmatch(r'(?:[A-Z])?\d{2,3}-[a-z0-9]+(?:-[a-z0-9]+)*', args.ticket):
        parser.error('Expected ticket number and lowercase hyphenated slug')
    try:
        root = Path(check(1024 ** 3)['root'])
        # Repository directory is discovered; product naming never becomes code configuration.
        repositories = list((root / 'git').glob('*.git'))
        if len(repositories) != 1:
            raise ValueError('Expected exactly one bare repository under STUDIO_ROOT/git')
        repo = repositories[0].resolve()
        if not repo.is_relative_to(root):
            raise ValueError('Bare repository resolves outside the studio volume')
        bare = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', '--is-bare-repository'], text=True).strip()
        if bare != 'true':
            raise ValueError('Repository must be bare')
        target = (root / 'worktrees' / args.ticket).resolve()
        if not target.is_relative_to(root) or target.exists():
            raise ValueError('Worktree target must be new and inside the studio volume')
        subprocess.run(['git', '-C', str(repo), 'worktree', 'add', str(target), '-b', f'ticket/{args.ticket}', 'integration'], check=True)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
