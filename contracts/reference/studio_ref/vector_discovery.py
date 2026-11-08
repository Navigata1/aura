"""Discover golden-vector producers/evaluators and validate the consumers manifest (vector kinds and record fields)."""
import importlib
import json
from pathlib import Path
import re

MANIFEST_KEYS = {'version', 'scope', 'consumers', 'records', 'pending'}


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
            or manifest['version'] != 2 or manifest['scope'] != 'vector-kinds and record fields'):
        raise ValueError('invalid vector consumers manifest')
    consumers = manifest['consumers']
    if not isinstance(consumers, dict) or set(consumers) != set(modules):
        raise ValueError('vector kinds and consumers must match exactly')
    slugs = known_tickets(root)
    for kind, tickets in consumers.items():
        check_tickets(kind, tickets, slugs)
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
    """A record kind is mapped field by field to real consuming tickets, or explicitly pending: a kind that predates
    T02b, whose consumer inventory is remaining T02 work. Orphan entries, unmapped fields and new kinds fail closed."""
    known = record_fields(root)
    if not isinstance(records, dict) or not isinstance(pending, list) or any(not isinstance(k, str) for k in pending):
        raise ValueError('invalid vector consumers manifest')
    for kind in sorted(set(records) | set(pending)):
        if kind not in known:
            raise ValueError(f'{kind}: orphan consumer entry (no such record kind)')
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
