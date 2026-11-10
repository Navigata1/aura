"""Hosted CI only: keep every disposable cache beneath the runner's temporary root.

This is not the local studio-volume adapter and must not be used on a personal host.
"""
import json
import os
from pathlib import Path
import sys

if os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('RUNNER_ENVIRONMENT')!='github-hosted':
    raise SystemExit('CI bootstrap requires a GitHub-hosted disposable runner')
root=Path(os.environ['RUNNER_TEMP'])/'studio'
root.mkdir(exist_ok=True)
paths={'STUDIO_ROOT':'','HF_HOME':'models/hf','HF_HUB_CACHE':'models/hf/hub','HF_XET_CACHE':'models/hf/xet','UV_CACHE_DIR':'envs/uv-cache','UV_PYTHON_INSTALL_DIR':'envs/python','UV_TOOL_DIR':'envs/uv-tools','UV_TOOL_BIN_DIR':'envs/uv-tools/bin','PIP_CACHE_DIR':'caches/pip','TORCH_HOME':'caches/torch','XDG_CACHE_HOME':'caches/xdg','XDG_DATA_HOME':'caches/xdg-data','XDG_STATE_HOME':'caches/xdg-state','npm_config_cache':'caches/npm','COREPACK_HOME':'caches/corepack','PLAYWRIGHT_BROWSERS_PATH':'caches/ms-playwright','TMPDIR':'scratch/tmp','TMP':'scratch/tmp','TEMP':'scratch/tmp','PNPM_HOME':'envs/pnpm'}
values={key:(root/value).as_posix() for key,value in paths.items()}
values.update({'UV_PYTHON_INSTALL_BIN':'0','UV_PYTHON_PREFERENCE':'only-managed','PYTHONDONTWRITEBYTECODE':'1','STUDIO_ENV':'test'})
Path(values['TMPDIR']).mkdir(parents=True,exist_ok=True)
with open(os.environ['GITHUB_ENV'],'a',encoding='utf-8') as out:
    for key,value in values.items():out.write(f'{key}={value}\n')
print('Disposable CI root: '+str(root))
