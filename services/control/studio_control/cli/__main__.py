"""The studioctl entry point. Commands register their own argument parser."""
import argparse
import importlib
import json
from pathlib import Path
import pkgutil
from studio_control import __version__
from studio_control.cli import commands


def product_name():
    for parent in Path(__file__).resolve().parents:
        product = parent / 'contracts/product.json'
        if product.is_file():
            return json.loads(product.read_text(encoding='utf-8'))['productName']
    raise RuntimeError('Product contract missing: run from an editable studio workspace')


def main(argv=None):
    parser = argparse.ArgumentParser(prog='studioctl')
    parser.add_argument('--version', action='version', version=f'{product_name()} {__version__}')
    subcommands = parser.add_subparsers(dest='command', required=True)
    for module in sorted(pkgutil.iter_modules(commands.__path__), key=lambda item: item.name):
        if module.name.startswith('_'):
            continue
        command = importlib.import_module(f'{commands.__name__}.{module.name}')
        command.register(subcommands.add_parser(module.name.replace('_', '-'), description=command.__doc__))
    args = parser.parse_args(argv)
    result = args.run(args)
    return result if isinstance(result, int) else 0


if __name__ == '__main__':
    raise SystemExit(main())
