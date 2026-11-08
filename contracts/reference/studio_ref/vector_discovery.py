"""Discover golden-vector producers/evaluators and validate their scoped consumers."""
import importlib
import json
from pathlib import Path
import re

ADDED = re.compile(r'added in 1\.[0-9]+\.[0-9]+')


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
    keys = set(manifest) if isinstance(manifest, dict) else set()
    if (not {'version', 'scope', 'consumers'} <= keys <= {'version', 'scope', 'consumers', 'fields'}
            or type(manifest['version']) is not int or manifest['version'] != 1 or manifest['scope'] != 'vector-kinds'):
        raise ValueError('invalid vector consumers manifest')
    consumers, fields = manifest['consumers'], manifest.get('fields', {})
    if not isinstance(consumers, dict) or set(consumers) != set(modules):
        raise ValueError('vector kinds and consumers must match exactly')
    if not isinstance(fields, dict):
        raise ValueError('invalid field consumers')
    added = added_fields(root)
    if set(fields) != added:
        raise ValueError(f'field consumers do not match added schema fields: missing {sorted(added - set(fields))}, '
                         f'orphan {sorted(set(fields) - added)}')
    slugs = {t['slug'] for t in json.loads((root / 'docs/spec/tickets.json').read_text(encoding='utf-8'))['tickets']}
    for kind, tickets in {**consumers, **fields}.items():
        if not isinstance(tickets, list) or not tickets or any(not isinstance(t, str) for t in tickets):
            raise ValueError(f'{kind}: missing consumer ticket slugs')
        if len(tickets) != len(set(tickets)) or not set(tickets) <= slugs:
            raise ValueError(f'{kind}: duplicate or unknown consumer ticket slug')
    return modules
