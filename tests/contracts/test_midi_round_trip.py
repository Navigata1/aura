"""The MIDI round-trip vectors through the public generator and contract gate, on a disposable tracked-file copy, and
the reference writer's typed error for arguments outside the schemas, which no schema-valid vector can carry."""
import copy
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
    ('one note', 'note(0, 960, 60, 100)', 'note(0, 959, 60, 100)'),             # a wrong MelodySpec note duration
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


def reference_midi():
    sys.path.insert(0, str(ROOT / 'contracts/reference'))
    try:
        from studio_ref import midi
    finally:
        sys.path.pop(0)
    return midi


class SmfWriteArgumentTests(unittest.TestCase):
    MELODY = {'tempo_map': {'tempo': [{'tick': 0, 'us_per_quarter': 500000}],
                            'meter': [{'tick': 0, 'numerator': 4, 'denominator': 4}]},
              'notes': [{'start_tick': 0, 'duration_ticks': 960, 'pitch': 60, 'velocity': 100}]}
    ASSEMBLED = {**MELODY, 'spec_kind': 'assembled',
                 'form': {'end_tick': 3840, 'sections': [{'name': 'verse', 'start_tick': 0}]}}

    def test_arguments_outside_the_schemas_raise_a_typed_error_instead_of_corrupt_bytes(self):
        midi = reference_midi()
        self.assertTrue(midi.to_smf(self.MELODY, [{'name': 'verse', 'tick': 0}]))  # the valid neighbour writes
        self.assertTrue(midi.to_smf(self.ASSEMBLED))  # and so does an assembled record, from its form
        spoilers = {
            'a meter denominator of 6': lambda m, k: m['tempo_map']['meter'][0].update(denominator=6),
            'a tempo of 2^24 us': lambda m, k: m['tempo_map']['tempo'][0].update(us_per_quarter=16777216),
            'a pitch of 200': lambda m, k: m['notes'][0].update(pitch=200),
            'a velocity of 0': lambda m, k: m['notes'][0].update(velocity=0),
            'a marker at tick -5': lambda m, k: k[0].update(tick=-5),
            'a marker name with a trailing newline': lambda m, k: k[0].update(name='verse\n'),
            'no tempo_map': lambda m, k: m.pop('tempo_map'),
            'a note without velocity': lambda m, k: m['notes'][0].pop('velocity'),
            'notes that are null': lambda m, k: m.update(notes=None),
            'a marker that is a string': lambda m, k: k.__setitem__(0, 'verse'),
            'a marker name with a lone surrogate': lambda m, k: k[0].update(name='verse\ud800'),
        }
        for label, spoil in spoilers.items():
            with self.subTest(label):
                melody, markers = copy.deepcopy(self.MELODY), [{'name': 'verse', 'tick': 0}]
                spoil(melody, markers)
                with self.assertRaises(midi.SmfWriteArgumentError):
                    midi.to_smf(melody, markers)
        with self.subTest('an end_tick of -1'), self.assertRaises(midi.SmfWriteArgumentError):
            midi.to_smf(self.MELODY, [], -1)
        for label, extra in {'markers beside a form': ([{'name': 'verse', 'tick': 0}], None),
                             'an end_tick beside a form': (None, 3840)}.items():
            with self.subTest(label), self.assertRaises(midi.SmfWriteArgumentError):
                midi.to_smf(self.ASSEMBLED, *extra)


if __name__ == '__main__':
    unittest.main()
