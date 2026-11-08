"""Exercise the shipped generator and validator CLI on disposable tracked copies."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class VectorDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='vector-contracts-')
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
        self.assertEqual(result.returncode == 0, ok, output)
        if contains:
            self.assertIn(contains, output)
        return output

    def install_probe(self):
        folder = self.root / 'contracts/reference/studio_ref/vector_cases'
        folder.mkdir(parents=True, exist_ok=True)
        (folder / 'probe.py').write_text('''KIND = "fixture.probe"
def build(profiles):
    return {"kind": KIND, "schemaVersion": "1.0.0", "cases": [{"name": "two plus three", "input": 2, "expected": 5}]}
def evaluate(case, world):
    return case["input"] + 3, case["expected"]
''')
        schema = {'type': 'object', 'required': ['kind', 'schemaVersion', 'cases'], 'additionalProperties': False,
                  'properties': {'kind': {'const': 'fixture.probe'}, 'schemaVersion': {'const': '1.0.0'},
                                 'cases': {'type': 'array', 'minItems': 1, 'items': {'type': 'object'}}}}
        (self.root / 'contracts/schemas/fixture-probe.schema.json').write_text(json.dumps(schema))
        manifest_path = self.root / 'contracts/consumers.json'
        manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {'version': 1, 'scope': 'vector-kinds', 'consumers': {}}
        manifest['consumers']['fixture.probe'] = ['contract-completion']
        manifest_path.write_text(json.dumps(manifest))
        return folder / 'probe.py', manifest_path

    def test_new_family_needs_no_shared_dispatch_edit(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in (self.root / 'contracts/fixtures').rglob('*.json')}
        self.install_probe()
        self.run_cli('contracts/reference/generate_fixtures.py')
        self.assertTrue((self.root / 'contracts/fixtures/vectors/probe.json').is_file())
        self.run_cli('scripts/spec/validate.py', '-v', contains='fixture.probe vectors')
        for path, data in before.items():
            self.assertEqual((self.root / path).read_bytes(), data, str(path))

    def test_bad_expected_value_is_not_accepted_by_generator_oracle(self):
        module, _ = self.install_probe()
        module.write_text(module.read_text().replace('"expected": 5', '"expected": 6'))
        self.run_cli('contracts/reference/generate_fixtures.py')
        self.run_cli('scripts/spec/validate.py', ok=False, contains='reference gives 5, fixture expects 6')

    def test_missing_evaluator_and_duplicate_kind_refuse_before_writes(self):
        module, _ = self.install_probe()
        original = module.read_text()
        for changed, message in [(original.replace('def evaluate(', 'def unused('), 'missing build or evaluate'),
                                 (original.replace('KIND = "fixture.probe"', 'KIND = "fixture.tempo"'), 'duplicate vector kind')]:
            with self.subTest(message=message):
                module.write_text(changed)
                self.run_cli('contracts/reference/generate_fixtures.py', ok=False, contains=message)
                self.run_cli('scripts/spec/validate.py', ok=False, contains=message)
                self.assertFalse((self.root / 'contracts/fixtures/vectors/probe.json').exists())

    def test_absent_or_unknown_consumer_refuses(self):
        _, manifest_path = self.install_probe()
        manifest = json.loads(manifest_path.read_text())
        for consumers, message in [(None, 'vector kinds and consumers must match'),
                                   ([], 'missing consumer ticket slugs'),
                                   (['not-a-ticket'], 'unknown consumer ticket slug')]:
            with self.subTest(consumers=consumers):
                if consumers is None:
                    manifest['consumers'].pop('fixture.probe', None)
                else:
                    manifest['consumers']['fixture.probe'] = consumers
                manifest_path.write_text(json.dumps(manifest))
                self.run_cli('contracts/reference/generate_fixtures.py', ok=False, contains=message)
                self.run_cli('scripts/spec/validate.py', ok=False, contains=message)

    def test_removed_handler_does_not_fall_through_to_another_evaluator(self):
        module, manifest_path = self.install_probe()
        self.run_cli('contracts/reference/generate_fixtures.py')
        module.unlink()
        manifest = json.loads(manifest_path.read_text())
        manifest['consumers'].pop('fixture.probe')
        manifest_path.write_text(json.dumps(manifest))
        self.run_cli('scripts/spec/validate.py', ok=False, contains='unknown vector kind: fixture.probe')

    def test_producer_cannot_write_a_different_kind(self):
        module, _ = self.install_probe()
        module.write_text(module.read_text().replace('"kind": KIND', '"kind": "fixture.unknown"'))
        self.run_cli('contracts/reference/generate_fixtures.py', ok=False, contains='producer kind mismatch')
        self.assertFalse((self.root / 'contracts/fixtures/vectors/probe.json').exists())

    def test_frozen_vector_expectations_still_execute_at_head(self):
        legacy = self.root / 'contracts/fixtures/legacy/1.0.0'
        legacy.mkdir(parents=True)
        vector = json.loads((self.root / 'contracts/fixtures/vectors/tempo.json').read_text())
        vector['cases'][0]['expected'] = 1
        (legacy / 'tempo.json').write_text(json.dumps(vector))
        self.run_cli('scripts/spec/validate.py', ok=False, contains='reference gives 0, fixture expects 1')

    def test_boolean_manifest_version_is_not_integer_version_one(self):
        _, manifest_path = self.install_probe()
        manifest = json.loads(manifest_path.read_text())
        manifest['version'] = True
        manifest_path.write_text(json.dumps(manifest))
        self.run_cli('contracts/reference/generate_fixtures.py', ok=False, contains='invalid vector consumers manifest')
        self.run_cli('scripts/spec/validate.py', ok=False, contains='invalid vector consumers manifest')

    def edit_manifest(self, change):
        path = self.root / 'contracts/consumers.json'
        manifest = json.loads(path.read_text())
        change(manifest)
        path.write_text(json.dumps(manifest))

    def test_record_consumers_refuse_orphans_gaps_and_unknown_tickets(self):
        original = (self.root / 'contracts/consumers.json').read_text()
        for change, message in [
                (lambda m: m['records']['benchmark-prereg'].update(no_such_field=['registry']), 'orphan consumer entry'),
                (lambda m: m['records'].update({'no-such-kind': {'id': ['registry']}}), 'orphan consumer entry'),
                (lambda m: m['records']['evidence-binding'].pop('membership_id'), 'field has no consumer'),
                (lambda m: m['records']['benchmark-membership'].update(cases=['not-a-ticket']), 'unknown consumer ticket slug'),
                (lambda m: m['records']['benchmark-prereg'].update(id=['C09']), 'unknown consumer ticket slug'),
                (lambda m: m['pending'].remove('verdict'), 'mapped or pending exactly once')]:
            with self.subTest(message=message):
                (self.root / 'contracts/consumers.json').write_text(original)
                self.edit_manifest(change)
                self.run_cli('contracts/reference/generate_fixtures.py', ok=False, contains=message)
                self.run_cli('scripts/spec/validate.py', ok=False, contains=message)

    def test_new_record_kind_needs_a_consumer_entry(self):
        schema = {'type': 'object', 'required': ['kind', 'schemaVersion'], 'additionalProperties': False,
                  'properties': {'kind': {'const': 'probe-record'}, 'schemaVersion': {'const': '1.0.0'}, 'note': {'type': 'string'}}}
        (self.root / 'contracts/schemas/probe-record.schema.json').write_text(json.dumps(schema))
        self.run_cli('scripts/spec/validate.py', ok=False, contains='probe-record: every record kind must be mapped or pending exactly once')
        self.edit_manifest(lambda m: m['records'].update({'probe-record': {'note': ['C02', 'registry']}}))
        self.run_cli('scripts/spec/validate.py')

    def test_binding_vectors_hold_hand_derived_findings(self):
        self.run_cli('scripts/spec/validate.py', '-v', contains='fixture.binding vectors')
        path = self.root / 'contracts/fixtures/vectors/binding.json'
        vector = json.loads(path.read_text())
        case = next(c for c in vector['cases'] if c['op'] == 'binding' and c['expected'] == [])
        case['expected'] = ['committed_after_run']
        path.write_text(json.dumps(vector))
        self.run_cli('scripts/spec/validate.py', ok=False, contains="reference gives [], fixture expects ['committed_after_run']")
