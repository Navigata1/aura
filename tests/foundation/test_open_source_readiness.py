"""The open-source-readiness register lists every release blocker of the component register (ADR-0011, T03)."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
REGISTER = ROOT / 'contracts/registry/components.v1.json'
OVERLAY = ROOT / 'scripts/registry/register_overlay.json'
EVIDENCE = ROOT / 'docs/research/evidence-register.json'
READINESS = ROOT / 'docs/research/licenses/open-source-readiness.json'

# T03 acceptance: these rows are release blockers, with these classes among theirs.
NAMED_BLOCKERS = {
    'yue2-3b': 'non_commercial_weights',
    'demucs-4.1.0': 'non_commercial_by_author',
    'demucs-mlx': 'non_commercial_by_author',
    'swiftf0': 'permissive_label_nc_data',
    'melband-roformer-kim': 'unverified_training_data',
    'basic-pitch': 'unverified_training_data',
}
# T03 acceptance: rows that cannot close today, each with the label the spec's Unverified capabilities table shows.
OPEN_ROWS = {
    'audio-decoder': 'Hums arrive as WAV only',
    'mp3-encoder': 'Export bundles carry WAV and MIDI only',
    'g2p-phonemizer': 'No lyric-error badge',
    'midi-synth-soundfont': 'No instrument rendering; NeutralVoice is the only guide',
    'lyric-aligner': 'No line or word replace',
}


def load_sync():
    spec = importlib.util.spec_from_file_location('registry_sync_readiness', ROOT / 'scripts/registry/sync.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


class OpenSourceReadinessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sync = load_sync()
        cls.register = read(REGISTER)
        cls.readiness = read(READINESS)
        cls.components = {c['id']: c for c in cls.register['components']}
        cls.entries = {e['id']: e for e in cls.readiness['release_blockers']}

    def test_committed_register_lists_every_release_blocker(self):
        self.assertEqual(self.sync.readiness_problems(self.register, self.readiness), [])

    def test_a_dropped_release_blocker_fails_the_check(self):
        dropped = copy.deepcopy(self.readiness)
        dropped['release_blockers'] = [e for e in dropped['release_blockers'] if e['id'] != 'basic-pitch']
        problems = self.sync.readiness_problems(self.register, dropped)
        self.assertTrue(any('basic-pitch' in p for p in problems), problems)

    def test_a_new_release_blocker_must_be_listed(self):
        planted = copy.deepcopy(self.register)
        next(c for c in planted['components'] if c['id'] == 'mido')['release_blockers'] = ['copyleft']
        problems = self.sync.readiness_problems(planted, self.readiness)
        self.assertTrue(any('mido' in p for p in problems), problems)

    def test_named_release_blockers_are_listed(self):
        for component_id, blocker_class in NAMED_BLOCKERS.items():
            self.assertIn(blocker_class, self.entries[component_id]['release_blockers'], component_id)

    def test_open_rows_name_their_gate_and_label_and_stay_research_only(self):
        for component_id, label in OPEN_ROWS.items():
            entry, row = self.entries[component_id], self.components[component_id]
            self.assertEqual(entry['label'], label, component_id)
            self.assertTrue(entry['gate'], component_id)
            self.assertIn('unverified', row['release_blockers'], component_id)
            self.assertEqual(row['allowed_lanes'], ['research'], component_id)
            self.assertIn(entry['gate'], row['verdict_condition'], component_id)
            self.assertIn(label, row['verdict_condition'], component_id)

    def test_no_row_leaves_unverified_without_a_primary_source(self):
        for row in self.register['components']:
            if row['verification_status'] != 'unverified':
                self.assertTrue(row['primary_sources'], row['id'])
        overlay = read(OVERLAY)
        overlay['license_verification']['rows']['mir-eval']['primary_sources'] = []
        with self.assertRaises(self.sync.SyncError):
            self.sync.build(read(EVIDENCE), overlay)

    def test_an_open_row_must_stay_unverified(self):
        overlay = read(OVERLAY)
        overlay['open_rows']['rows']['mir-eval'] = {'gate': 'a gate', 'label': 'a label'}
        with self.assertRaises(self.sync.SyncError):
            self.sync.build(read(EVIDENCE), overlay)

    def test_readiness_register_regenerates_byte_identically(self):
        json_bytes, markdown_bytes = self.sync.generate_readiness()
        self.assertEqual(json_bytes, READINESS.read_bytes())
        self.assertEqual(markdown_bytes, READINESS.with_suffix('.md').read_bytes())


if __name__ == '__main__':
    unittest.main()
