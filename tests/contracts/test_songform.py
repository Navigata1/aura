"""SongForm vectors and added-field consumers, through the shipped generator and validator CLIs on tracked copies."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
CHORDS = 'song-spec.schema.json#/properties/form/properties/sections/items/properties/chord_symbols'


class SongFormContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='songform-contracts-')
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

    def test_vectors_pass_and_a_seeded_wrong_onset_fails(self):
        self.run_cli('scripts/spec/validate.py', '-v', contains='fixture.songform vectors')
        cases = self.root / 'contracts/reference/studio_ref/vector_cases/songform.py'
        text = cases.read_text()
        self.assertEqual(text.count('(6720, 480, 67, 90)'), 1)
        cases.write_text(text.replace('(6720, 480, 67, 90)', '(6721, 480, 67, 90)'))
        self.run_cli('contracts/reference/generate_fixtures.py')
        self.run_cli('scripts/spec/validate.py', '-v', ok=False, contains='contracts/fixtures/vectors/songform.json [intro, pickup')

    def test_added_fields_and_their_consumers_match_both_ways(self):
        manifest_path = self.root / 'contracts/consumers.json'
        schema_path = self.root / 'contracts/schemas/song-spec.schema.json'
        manifest, schema = manifest_path.read_text(), schema_path.read_text()
        annotated = json.loads(schema)
        annotated['properties']['references']['$comment'] = 'added in 1.2.0'
        for name, fields, song_schema, message in [
                ('field without consumer', lambda f: f.pop(CHORDS), schema, 'missing'),
                ('orphan consumer', lambda f: f.update({'song-spec.schema.json#/properties/rev': ['song-spec']}), schema, 'orphan'),
                ('unknown ticket slug', lambda f: f.update({CHORDS: ['not-a-ticket']}), schema, 'unknown consumer ticket slug'),
                ('newly added field', lambda f: None, json.dumps(annotated), 'song-spec.schema.json#/properties/references')]:
            with self.subTest(name):
                changed = json.loads(manifest)
                fields(changed['fields'])
                manifest_path.write_text(json.dumps(changed))
                schema_path.write_text(song_schema)
                self.run_cli('contracts/reference/generate_fixtures.py', ok=False, contains=message)
                self.run_cli('scripts/spec/validate.py', ok=False, contains=message)
