"""Training-data provenance reviews decide their register rows' llc eligibility (ADR-0011 rule 6, T54).

A review lists every input the shipped model was trained on, each with its terms from a pinned and hashed primary
source. It passes only when every input's terms were found and permit commercial use: an input whose terms cannot be
found fails the review as unverifiable. The register row then follows the review: llc only after a pass, a
training-data release blocker that llc forbids after a fail. Interpretation, not legal advice.
"""
import copy
import importlib.util
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
REVIEWS = ROOT / 'docs/research/licenses/provenance-reviews'
REGISTER = ROOT / 'contracts/registry/components.v1.json'
LANES = ROOT / 'contracts/registry/lanes.v1.json'
OVERLAY = ROOT / 'scripts/registry/register_overlay.json'
EVIDENCE = ROOT / 'docs/research/evidence-register.json'

# T54 reviews these components; any later review adds its own record here.
REVIEWED = {'swiftf0', 'basic-pitch'}
KIND = 'training-data-provenance-review'
LEGAL_LABEL = 'Interpretation, not legal advice.'
COMMERCIAL_USE = {'permitted', 'not_permitted', 'unverifiable'}
# Which release-blocker class each finding puts on the row; a pass leaves neither.
CLASS_FOR = {'not_permitted': 'permissive_label_nc_data', 'unverifiable': 'unverified_training_data'}
RECORD_ID = re.compile(r'^prv_[a-z0-9][a-z0-9.-]{0,62}$')
URL = re.compile(r'^https?://\S+$')
SHA256 = re.compile(r'^[0-9a-f]{64}$')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def load_sync():
    spec = importlib.util.spec_from_file_location('registry_sync_provenance', ROOT / 'scripts/registry/sync.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def decided_verdict(review):
    """The verdict the training inputs decide: pass only when every input's terms permit commercial use."""
    uses = [entry['terms']['commercial_use'] for entry in review['training_inputs']]
    return 'pass' if uses and all(use == 'permitted' for use in uses) else 'fail'


def record_problems(review):
    """A complete record: every input cites where it is trained on and its terms, each source pinned and hashed."""
    rid = review.get('id', '?')
    problems = [] if RECORD_ID.match(rid) else [f'{rid}: record id must match {RECORD_ID.pattern}']
    if review.get('kind') != KIND or review.get('legal_label') != LEGAL_LABEL:
        problems.append(f'{rid}: needs kind {KIND!r} and the label {LEGAL_LABEL!r}')
    sources = review.get('sources') or {}
    for sid, source in sources.items():
        if not (URL.match(source.get('url', '')) and SHA256.match(source.get('sha256', ''))
                and source.get('document') and source.get('pin')):
            problems.append(f'{rid}: source {sid!r} needs a document, a URL, a SHA-256 and a pin')
    inputs = review.get('training_inputs') or []
    if not inputs:
        problems.append(f'{rid}: lists no training inputs')
    for entry in inputs:
        name, terms = entry.get('name', '?'), entry.get('terms') or {}
        if terms.get('commercial_use') not in COMMERCIAL_USE or not terms.get('reading'):
            problems.append(f'{rid}: {name} needs a terms reading and a commercial_use in {sorted(COMMERCIAL_USE)}')
        cited = [terms.get('source')] + list(entry.get('listed_in') or [])
        if not entry.get('listed_in') or any(sid not in sources for sid in cited):
            problems.append(f'{rid}: {name} must cite known sources for its terms and for its use in training')
    if inputs and not problems:
        if review.get('verdict') != decided_verdict(review):
            problems.append(f"{rid}: verdict {review.get('verdict')!r}, but its training inputs decide "
                            f'{decided_verdict(review)!r}')
        blocking = sorted(e['name'] for e in inputs if e['terms']['commercial_use'] != 'permitted')
        if sorted(review.get('decided_by') or []) != blocking:
            problems.append(f'{rid}: decided_by must name exactly the inputs that block a pass: {blocking}')
        stated = review.get('register') or {}
        if (('llc' in (stated.get('allowed_lanes') or [])) != (decided_verdict(review) == 'pass')
                or sorted(stated.get('training_data_release_blockers') or []) != decided_classes(review)):
            problems.append(f'{rid}: its register statement must match what its training inputs decide')
    return problems


def decided_classes(review):
    """The training-data release-blocker classes a review puts on its row (none after a pass)."""
    return sorted({CLASS_FOR[e['terms']['commercial_use']] for e in review['training_inputs']
                   if e['terms']['commercial_use'] in CLASS_FOR})


def register_problems(review, register, lane_policy):
    """The row's lanes and training-data classes are exactly what the review decides, and the row cites it."""
    rid, cid = review['id'], review['component_id']
    row = next((c for c in register['components'] if c['id'] == cid), None)
    if row is None:
        return [f'{rid}: the register has no row {cid!r}']
    llc_forbids = set(next(lane for lane in lane_policy['lanes'] if lane['id'] == 'llc')['forbidden_release_blockers'])
    expected = set(decided_classes(review))
    problems = []
    if review['verdict'] == 'pass' and 'llc' not in row['allowed_lanes']:
        problems.append(f'{cid}: {rid} passed, so the row must allow llc')
    if review['verdict'] == 'fail' and 'llc' in row['allowed_lanes']:
        problems.append(f'{cid}: {rid} failed, so the row may not allow llc')
    if review['verdict'] == 'fail' and not set(row['release_blockers']) & llc_forbids:
        problems.append(f'{cid}: {rid} failed, so the row needs a release blocker that llc forbids')
    found = set(row['release_blockers']) & set(CLASS_FOR.values())
    if found != expected:
        problems.append(f'{cid}: {rid} decides the training-data classes {sorted(expected)}, the row has {sorted(found)}')
    if rid not in (row['verdict_condition'] or ''):
        problems.append(f'{cid}: the verdict condition must cite {rid}')
    return problems


class ProvenanceReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sync = load_sync()
        cls.register = read(REGISTER)
        cls.lanes = read(LANES)
        cls.reviews = {path.name: read(path) for path in sorted(REVIEWS.glob('*.json'))}

    def review_of(self, component_id):
        return next(r for r in self.reviews.values() if r.get('component_id') == component_id)

    def test_each_reviewed_component_has_exactly_one_record(self):
        components = sorted(r.get('component_id') for r in self.reviews.values())
        self.assertEqual(components, sorted(REVIEWED))
        self.assertEqual(len({r.get('id') for r in self.reviews.values()}), len(self.reviews))

    def test_records_are_complete_and_their_verdicts_follow_the_inputs(self):
        for name, review in self.reviews.items():
            self.assertEqual(record_problems(review), [], name)

    def test_register_rows_follow_their_reviews(self):
        for name, review in self.reviews.items():
            self.assertEqual(register_problems(review, self.register, self.lanes), [], name)

    def test_unverifiable_terms_never_pass(self):
        review = copy.deepcopy(self.review_of('swiftf0'))
        for entry in review['training_inputs']:
            entry['terms']['commercial_use'] = 'permitted'
        self.assertEqual(decided_verdict(review), 'pass')
        review['training_inputs'][0]['terms']['commercial_use'] = 'unverifiable'
        self.assertEqual(decided_verdict(review), 'fail')
        review['verdict'], review['decided_by'] = 'pass', []
        self.assertTrue(any('decide' in p for p in record_problems(review)), record_problems(review))

    def test_an_input_without_a_hashed_terms_source_is_caught(self):
        review = copy.deepcopy(self.review_of('basic-pitch'))
        sid = review['training_inputs'][0]['terms']['source']
        review['sources'][sid]['sha256'] = ''
        self.assertTrue(record_problems(review))
        review = copy.deepcopy(self.review_of('basic-pitch'))
        review['training_inputs'][0]['terms']['source'] = 'not-a-source'
        self.assertTrue(record_problems(review))

    def test_a_row_widened_to_llc_against_a_failed_review_is_caught(self):
        overlay = read(OVERLAY)
        overlay['allowed_lanes_override']['swiftf0']['lanes'] = ['individual', 'llc', 'research']
        overlay['release_blockers']['permissive_label_nc_data'].remove('swiftf0')
        widened = {'components': self.sync.build(read(EVIDENCE), overlay)}
        problems = register_problems(self.review_of('swiftf0'), widened, self.lanes)
        self.assertTrue(any('may not allow llc' in p for p in problems), problems)

    def test_a_passed_review_must_widen_its_row(self):
        review = copy.deepcopy(self.review_of('basic-pitch'))
        for entry in review['training_inputs']:
            entry['terms']['commercial_use'] = 'permitted'
        review['verdict'], review['decided_by'] = 'pass', []
        problems = register_problems(review, self.register, self.lanes)
        self.assertTrue(any('must allow llc' in p for p in problems), problems)


if __name__ == '__main__':
    unittest.main()
