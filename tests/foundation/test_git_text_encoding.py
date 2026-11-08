"""Real Git subprocess policy scans under a non-UTF-8 Python default."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
CHECK = ROOT / 'scripts/ci/check.py'


class GitTextEncodingTest(unittest.TestCase):
    def exercise_policy(self, filename, content, message):
        with tempfile.TemporaryDirectory(prefix='git-encoding-') as temporary:
            root = Path(temporary)
            env = {**os.environ, 'PYTHONUTF8': '0', 'PYTHONCOERCECLOCALE': '0', 'LC_ALL': 'C',
                   'PYTHONIOENCODING': 'ascii', 'GIT_AUTHOR_NAME': 'Synthetic', 'GIT_COMMITTER_NAME': 'Synthetic',
                   'GIT_AUTHOR_EMAIL': '1+Navigata1'+'@'+'users.noreply.github.com',
                   'GIT_COMMITTER_EMAIL': '1+Navigata1'+'@'+'users.noreply.github.com'}
            probe = subprocess.check_output([sys.executable, '-c',
                'import json,locale,sys; print(json.dumps([sys.flags.utf8_mode,locale.getencoding()]))'], env=env, encoding='ascii')
            mode, encoding = json.loads(probe)
            self.assertEqual(mode, 0)
            if os.name != 'nt':
                self.assertNotEqual(encoding.lower().replace('-', ''), 'utf8')
            def git(*args):
                return subprocess.check_output(['git', '-C', temporary, *args], env=env, encoding='utf-8')
            git('init', '-q')
            (root / 'contracts').mkdir()
            product = json.loads((ROOT / 'contracts/product.json').read_text(encoding='utf-8'))
            (root / 'contracts/product.json').write_text(json.dumps(product), encoding='utf-8')
            git('add', '-A'); git('commit', '-qm', 'Baseline')
            base = git('rev-parse', 'HEAD').strip()
            # UTF-8 curly quotes contain byte 0x9d, which is undefined in cp1252.
            note = root / filename
            note.write_text(content, encoding='utf-8')
            git('add', '-A'); git('commit', '-qm', message)
            def scan():
                return subprocess.run([sys.executable, str(CHECK), '--root', temporary, '--base', base],
                                      env=env, capture_output=True, encoding='ascii')
            result = scan()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            note.write_text('\u201cEvidence\u201d\n' + 'ghp_' + 'A' * 36, encoding='utf-8')
            result = scan()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('secret: credential-shaped content', result.stdout)
            self.assertIn('PR diff', result.stdout)
            self.assertTrue(any('secret: credential-shaped content' in line and not line.startswith('PR diff:')
                                for line in result.stdout.splitlines()), result.stdout)
            self.assertNotIn('Unicode', result.stderr)
            self.assertNotIn('A' * 36, result.stdout + result.stderr)

            # Invalid text bytes must not hide an ASCII credential-shaped diff.
            note.write_bytes(b'\xff' + b'ghp_' + b'B' * 36)
            result = scan()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('PR diff: secret: credential-shaped content', result.stdout)
            self.assertNotIn('B' * 36, result.stdout + result.stderr)

            # Neither Unicode text nor a Unicode filename may hide a home path; its account is never echoed.
            note.write_text('\u201cEvidence\u201d ' + '/'.join(['', 'home', 'someone', 'notes.txt']) + '\n', encoding='utf-8')
            result = scan()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('private-path: line 1:', result.stdout)
            self.assertNotIn('someone', result.stdout + result.stderr)

    def test_unicode_git_inputs_keep_policy_checks_effective(self):
        for filename, content, message in [
            ('notes.md', '\u201cUnicode evidence\u201d\n', 'ASCII subject'),
            ('notes-\u4e2d.md', 'ASCII text\n', 'ASCII subject'),
            ('notes.md', 'ASCII text\n', 'Record \u201cevidence\u201d'),
        ]:
            with self.subTest(filename=filename, content=content, message=message):
                self.exercise_policy(filename, content, message)
