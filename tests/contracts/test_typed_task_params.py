"""Well-formed 1.1.0 task requests validate (the invalid-record fixtures pin each refusal), and 1.0.0 stays untyped."""
import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/spec'))
from jsonschema_subset import SchemaSet  # noqa: E402

HASH = 'a' * 64


def request(task, profile, inputs, version='1.1.0', **params):
    return {'kind': 'task-request', 'schemaVersion': version, 'job_id': 'job_t', 'profile_id': profile, 'task': task,
            'lane': 'individual', 'inputs': [{'role': r, 'sha256': HASH, 'media_type': m, 'bytes': 1} for r, m in inputs],
            'params': params, 'seed': None, 'deadline_s': 600}


GENERATE = {'duration_s': 30, 'channels': 2, 'lyrics_language': None}
FAULTS = {'drift_cents': -30, 'octave_error_rate': '0.25', 'onset_jitter_ms': 20, 'clip_db': 6, 'silence': False,
          'fail_at_step': 2, 'crash_at': 'loading', 'wrong_output_hash': True, 'slow_load_ms': 100, 'ignore_cancel': True,
          'refuse': 'busy'}
VALID = {
    'instrumental cover of a guide': request('cover', 'ace-2b-turbo-mlx', [('source', 'audio/wav')], **GENERATE),
    'sung cover of a FLAC hum': request('cover', 'ace-2b-turbo-mlx', [('source', 'audio/flac'), ('lyrics', 'text/plain')],
                                        **{**GENERATE, 'lyrics_language': 'en', 'audio_cover_strength': '1.0'}),
    'text to song with style and every fault': request('text_to_song', 'fake-route-a', [('style', 'text/plain')],
                                                       **GENERATE, faults=FAULTS),
    'sung text to song': request('text_to_song', 'fake-route-b', [('lyrics', 'text/plain')], **{**GENERATE, 'lyrics_language': 'en'}),
    'guide with every voice param': request('guide', 'analysis-guide-neutralvoice', [('melody', 'application/json')],
                                            sample_rate=44100, vowel='o', vibrato_cents=100, drift_cents=30),
    'untyped task with no params': request('separate', 'fake-separate', [('mix', 'audio/wav')]),
    '1.0.0 keeps free params': request('cover', 'fake-route-a', [('guide', 'audio/wav')], version='1.0.0', audio_cover_strength='0.9'),
}


class TypedTaskParamsTests(unittest.TestCase):
    schemas = SchemaSet(ROOT / 'contracts/schemas')

    def test_well_formed_requests_validate(self):
        for name, record in VALID.items():
            with self.subTest(name):
                self.assertEqual(self.schemas.validate(copy.deepcopy(record), 'task-request.schema.json'), [])

    def test_the_same_requests_at_1_1_refuse_an_extra_param(self):
        for name, record in VALID.items():
            if record['schemaVersion'] == '1.0.0':
                continue
            with self.subTest(name):
                extra = copy.deepcopy(record)
                extra['params']['unknown'] = 1
                self.assertTrue(self.schemas.validate(extra, 'task-request.schema.json'))


if __name__ == '__main__':
    unittest.main()
