"""Print shell exports only after the storage preflight succeeds."""
import os
import shlex
import sys
from preflight import check


def exports():
    if os.environ.get('UV_PROJECT_ENVIRONMENT'):
        raise ValueError('UV_PROJECT_ENVIRONMENT must not be exported in the development shell')
    if sys.platform == 'darwin':
        os.environ.setdefault('STUDIO_ROOT', '/Volumes/STUDIO')
    root = check()['root']
    paths = {
        'STUDIO_ROOT': '', 'STUDIO_STORE_ROOT': 'projects',
        'HF_HOME': 'models/hf', 'HF_HUB_CACHE': 'models/hf/hub', 'HF_XET_CACHE': 'models/hf/xet',
        'UV_CACHE_DIR': 'envs/uv-cache', 'UV_PYTHON_INSTALL_DIR': 'envs/python',
        'UV_TOOL_DIR': 'envs/uv-tools', 'UV_TOOL_BIN_DIR': 'envs/uv-tools/bin',
        'PIP_CACHE_DIR': 'caches/pip', 'TORCH_HOME': 'caches/torch',
        'XDG_CACHE_HOME': 'caches/xdg', 'XDG_DATA_HOME': 'caches/xdg-data', 'XDG_STATE_HOME': 'caches/xdg-state',
        'npm_config_cache': 'caches/npm', 'COREPACK_HOME': 'caches/corepack',
        'PLAYWRIGHT_BROWSERS_PATH': 'caches/ms-playwright', 'TMPDIR': 'scratch/tmp',
        'TMP': 'scratch/tmp', 'TEMP': 'scratch/tmp', 'PNPM_HOME': 'envs/pnpm',
    }
    values = {name: root + ('/' + path if path else '') for name, path in paths.items()}
    values.update({'UV_PYTHON_INSTALL_BIN': '0', 'UV_PYTHON_PREFERENCE': 'only-managed', 'PYTHONDONTWRITEBYTECODE': '1', 'STUDIO_ENV': os.environ.get('STUDIO_ENV', 'dev')})
    from pathlib import Path
    for name in paths:
        if not Path(values[name]).resolve().is_relative_to(Path(root)):
            raise ValueError(f'{name} escapes the studio volume through a symlink')
    os.makedirs(values['TMPDIR'], exist_ok=True)
    return values


if __name__ == '__main__':
    try:
        values = exports()
        if '--json' in sys.argv:
            import json
            print(json.dumps(values))
        else:
            for key, value in values.items():
                print(f'export {key}={shlex.quote(value)}')
    except Exception as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
