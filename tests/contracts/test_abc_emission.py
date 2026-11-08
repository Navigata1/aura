"""YuE2 ABC emission vectors (T02e), through the shipped generator and validator CLIs on tracked copies."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
CASES = 'contracts/reference/studio_ref/vector_cases/abc.py'


class AbcEmissionContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='abc-contracts-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT, text=True).split('\0')
        for name in tracked:
            if name and (ROOT / name).is_file():
                target = self.root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)

    def run_cli(self, path, *args, ok=True, contains=None):
        result = subprocess.run([sys.executable, path, *args], cwd=self.root, text=True, capture_output=True)
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode == 0, ok, output[-4000:])
        if contains:
            self.assertIn(contains, output)
        return output

    def seed(self, old, new):
        """Plant one wrong hand-derived expectation in the case module and regenerate the fixtures from it."""
        cases = self.root / CASES
        text = cases.read_text(encoding='utf-8')
        self.assertEqual(text.count(old), 1, old)
        cases.write_text(text.replace(old, new), encoding='utf-8')
        self.run_cli('contracts/reference/generate_fixtures.py')

    def test_vectors_pass_the_gate(self):
        self.run_cli('scripts/spec/validate.py', '-v', contains='fixture.abc vectors')

    def test_a_seeded_wrong_bar_fails(self):
        # The re-quantized half-note triplet bar of the pickup case, which the stripped-chords case also expects.
        self.seed('A8-A2G8-G3|Z|', 'A8-A3G8-G3|Z|')
        # The validator prints OS-native paths, so match the file name, case name and mismatch, not the separators.
        self.run_cli('scripts/spec/validate.py', '-v', ok=False,
                     contains='abc.json [pickup, half-note triplet, intro and outro]: reference gives')

    def test_a_seeded_wrong_reason_fails(self):
        self.seed('"length_over_limit"', '"lyrics_language"')
        self.run_cli('scripts/spec/validate.py', '-v', ok=False,
                     contains='abc.json [a 6 min 30 s form is over the limit]: reference gives')
