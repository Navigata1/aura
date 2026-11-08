"""The MIDI round-trip vectors through the public generator and contract gate, on a disposable tracked-file copy."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
CASES = 'contracts/reference/studio_ref/vector_cases/midi.py'
# Each edit seeds one wrong hand-derived expectation into the case module (first occurrence only).
SEEDED = [
    ('one note', '"00903c64"', '"00903c65"'),                                  # a wrong byte: note-on velocity 101
    ('one note', 'note(0, 960, 60, 100)', 'note(0, 961, 60, 100)'),             # a wrong MelodySpec note duration
    ('SMPTE', '"smpte_division", None, None', '"malformed_smf", None, None'),   # a wrong typed refusal
]


class MidiRoundTripGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='midi-contracts-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT, text=True).split('\0')
        for name in tracked:
            if name and (ROOT / name).is_file():
                target = self.root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)

    def run_cli(self, *args):
        result = subprocess.run([sys.executable, *args], cwd=self.root, text=True, capture_output=True)
        return result.returncode, result.stdout + result.stderr

    def test_hand_derived_vectors_pass_and_each_seeded_wrong_expectation_fails(self):
        code, out = self.run_cli('scripts/spec/validate.py', '-v')
        self.assertEqual(code, 0, out)
        self.assertRegex(out, r'ok +\d+  fixture\.midi vectors')
        module = self.root / CASES
        original = module.read_text(encoding='utf-8')
        for case, old, new in SEEDED:
            with self.subTest(case=case, seeded=new):
                self.assertIn(old, original)
                module.write_text(original.replace(old, new, 1), encoding='utf-8')
                try:
                    code, out = self.run_cli('contracts/reference/generate_fixtures.py')
                    self.assertEqual(code, 0, out)  # the generator writes the expectation; it never asks the reference
                    code, out = self.run_cli('scripts/spec/validate.py', '-v')
                    self.assertNotEqual(code, 0, out)
                    # The gate prints the fixture path with the host's separator, so match from the file name on.
                    self.assertRegex(out, rf'midi\.json \[[^\]]*{case}[^\]]*\]: reference gives')
                finally:
                    module.write_text(original, encoding='utf-8')


if __name__ == '__main__':
    unittest.main()
