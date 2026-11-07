"""Discover golden-vector producers/evaluators and validate their scoped consumers."""
import importlib
import json
from pathlib import Path
import re


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
    if (not isinstance(manifest, dict) or set(manifest) != {'version', 'scope', 'consumers'}
            or type(manifest['version']) is not int or manifest['version'] != 1 or manifest['scope'] != 'vector-kinds'):
        raise ValueError('invalid vector consumers manifest')
    consumers = manifest['consumers']
    if not isinstance(consumers, dict) or set(consumers) != set(modules):
        raise ValueError('vector kinds and consumers must match exactly')
    slugs = {t['slug'] for t in json.loads((root / 'docs/spec/tickets.json').read_text(encoding='utf-8'))['tickets']}
    for kind, tickets in consumers.items():
        if not isinstance(tickets, list) or not tickets or any(not isinstance(t, str) for t in tickets):
            raise ValueError(f'{kind}: missing consumer ticket slugs')
        if len(tickets) != len(set(tickets)) or not set(tickets) <= slugs:
            raise ValueError(f'{kind}: duplicate or unknown consumer ticket slug')
    return modules
