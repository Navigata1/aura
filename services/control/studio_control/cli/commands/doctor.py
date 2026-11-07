"""Report available diagnostic sections. Empty does not mean hardware is verified."""
import importlib
import json
import pkgutil
from studio_control.cli import doctor


def run(args):
    sections = {}
    for module in sorted(pkgutil.iter_modules(doctor.__path__), key=lambda item: item.name):
        if not module.name.startswith('_'):
            section = importlib.import_module(f'{doctor.__name__}.{module.name}')
            sections[module.name] = section.inspect()
    print(json.dumps(sections, indent=2, sort_keys=True))


def register(parser):
    parser.set_defaults(run=run)
