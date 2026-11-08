"""Discover golden-vector producers/evaluators and validate the consumers manifest: vector kinds, the fields of record
kinds new since T02b (older kinds sit on a frozen pending allow-list) and fields that a minor version added."""
import importlib
import json
from pathlib import Path
import re

ADDED = re.compile(r'added in 1\.[1-9][0-9]*\.[0-9]+')  # a minor version above 1.0.0
MANIFEST_KEYS = {'version', 'scope', 'consumers', 'fields', 'records', 'pending'}
SCOPE = 'vector-kinds, record fields and added fields'
# The record kinds that predate T02b (integration 7cb7bbd). pending may only shrink: a kind leaves it by being mapped
# field by field in records, and no new kind can be parked on it.
PRE_T02B_RECORD_KINDS = frozenset({
    'approval', 'artifact', 'audition', 'burst-run', 'candidate', 'capability-registry', 'component-register', 'compute-profile',
    'compute-tiers', 'correction-log', 'edit-operation', 'engine-profile-registry', 'eval-brief', 'eval-set', 'event', 'evidence',
    'export-manifest', 'generation-request', 'hardware-snapshot', 'import-terms', 'job', 'keeper', 'lane-policy', 'ledger-entry',
    'license-acceptance', 'melody-spec', 'prereg', 'product', 'project', 'provenance-sidecar', 'quote', 'reference', 'refusal',
    'reveal', 'risk-acceptance', 'session', 'song-spec', 'store', 'task-request', 'task-status', 'timeline', 'verdict',
    'worker-describe', 'worker-health'})


def added_fields(root: Path) -> set[str]:
    """Every schema location a minor version added, marked with the annotation $comment 'added in 1.x.y'."""
    found = set()

    def walk(node, where):
        if isinstance(node, dict):
            if isinstance(node.get('$comment'), str) and ADDED.fullmatch(node['$comment']):
                found.add(where)
            for key, value in node.items():
                walk(value, f'{where}/{key}')
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, f'{where}/{index}')
    for path in sorted((root / 'contracts/schemas').glob('*.schema.json')):
        walk(json.loads(path.read_text(encoding='utf-8')), f'{path.name}#')
    return found


def discover(root: Path):
    modules = {}
    directory = root / 'contracts/reference/studio_ref/vector_cases'
    for path in sorted(directory.glob('*.py')):
        if path.name.startswith('_'):
            continue
        module = importlib.import_module(f'studio_ref.vector_cases.{path.stem}')
        kind = getattr(module, 'KIND', None)
        if not isinstance(kind, str) or not re.fullmatch(r'fixture\.[a-z][a-z0-9-]*', kind):
            raise ValueError(f'{path.name}: invalid vector KIND')
        if kind in modules:
            raise ValueError(f'duplicate vector kind: {kind}')
        if not callable(getattr(module, 'build', None)) or not callable(getattr(module, 'evaluate', None)):
            raise ValueError(f'{kind}: missing build or evaluate callable')
        modules[kind] = module
    if not modules:
        raise ValueError('no vector case modules discovered')
    manifest = json.loads((root / 'contracts/consumers.json').read_text(encoding='utf-8'))
    if (not isinstance(manifest, dict) or set(manifest) != MANIFEST_KEYS or type(manifest['version']) is not int
            or manifest['version'] != 2 or manifest['scope'] != SCOPE):
        raise ValueError('invalid vector consumers manifest')
    consumers, fields = manifest['consumers'], manifest['fields']
    if not isinstance(consumers, dict) or set(consumers) != set(modules):
        raise ValueError('vector kinds and consumers must match exactly')
    if not isinstance(fields, dict):
        raise ValueError('invalid field consumers')
    added = added_fields(root)
    if set(fields) != added:
        raise ValueError(f'field consumers do not match added schema fields: missing {sorted(added - set(fields))}, '
                         f'orphan {sorted(set(fields) - added)}')
    slugs = known_tickets(root)
    for name, tickets in {**consumers, **fields}.items():
        check_tickets(name, tickets, slugs)
    check_records(root, manifest['records'], manifest['pending'], slugs)
    return modules


def known_tickets(root: Path) -> set:
    """Slugs of docs/spec/tickets.json plus the contract-fix ids registered by a docs/spec/contract-fixes/Cnn-*.md file."""
    slugs = {t['slug'] for t in json.loads((root / 'docs/spec/tickets.json').read_text(encoding='utf-8'))['tickets']}
    return slugs | {path.name[:3] for path in (root / 'docs/spec/contract-fixes').glob('C[0-9][0-9]-*.md')}


def check_tickets(name: str, tickets, slugs: set) -> None:
    if not isinstance(tickets, list) or not tickets or any(not isinstance(t, str) for t in tickets):
        raise ValueError(f'{name}: missing consumer ticket slugs')
    if len(tickets) != len(set(tickets)) or not set(tickets) <= slugs:
        raise ValueError(f'{name}: duplicate or unknown consumer ticket slug')


def record_fields(root: Path) -> dict:
    """Every record kind a schema declares (fixture kinds aside) and its top-level fields, kind and schemaVersion aside."""
    fields = {}
    for path in sorted((root / 'contracts/schemas').glob('*.schema.json')):
        schema = json.loads(path.read_text(encoding='utf-8'))
        kind = schema.get('properties', {}).get('kind', {})
        for name in [kind['const']] if 'const' in kind else kind.get('enum', []):
            if not name.startswith('fixture.'):
                fields[name] = set(schema['properties']) - {'kind', 'schemaVersion'}
    return fields


def check_records(root: Path, records, pending, slugs: set) -> None:
    """Each record kind is either mapped field by field (top-level fields) to real consuming tickets, or pending: one of
    PRE_T02B_RECORD_KINDS, whose consumer inventory is remaining T02 work. pending can only shrink. An orphan kind or
    field entry, an unmapped field, a kind on neither list or on both, and a new kind parked on pending all fail closed."""
    known = record_fields(root)
    if not isinstance(records, dict) or not isinstance(pending, list) or any(not isinstance(k, str) for k in pending):
        raise ValueError('invalid vector consumers manifest')
    for kind in sorted(set(records) | set(pending)):
        if kind not in known:
            raise ValueError(f'{kind}: orphan consumer entry (no such record kind)')
    parked = sorted(set(pending) - PRE_T02B_RECORD_KINDS)
    if parked:
        raise ValueError(f'{parked[0]}: pending is frozen to the record kinds that predate T02b; map its fields in records')
    for kind in sorted(known):
        if int(kind in records) + pending.count(kind) != 1:
            raise ValueError(f'{kind}: every record kind must be mapped or pending exactly once')
    for kind, fields in sorted(records.items()):
        if not isinstance(fields, dict):
            raise ValueError(f'{kind}: field consumers must be an object')
        orphans, unmapped = sorted(set(fields) - known[kind]), sorted(known[kind] - set(fields))
        if orphans:
            raise ValueError(f'{kind}.{orphans[0]}: orphan consumer entry (no such field)')
        if unmapped:
            raise ValueError(f'{kind}.{unmapped[0]}: field has no consumer')
        for field, tickets in sorted(fields.items()):
            check_tickets(f'{kind}.{field}', tickets, slugs)
