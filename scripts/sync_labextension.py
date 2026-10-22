"""Install the freshly built frontend before JupyterLite discovers extensions.

An existing editable Python install may contain an older shared-data copy.
Copy without removing unrelated extensions; package.json selects the new hashes.
"""
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent


def main():
    source = ROOT / 'al_engine/labextension'
    package = json.loads((source / 'package.json').read_text(encoding='utf-8'))
    load = package['jupyterlab']['_build']['load']
    if not (source / load).is_file():
        raise ValueError('Build the labextension before syncing it.')
    target = Path(sys.prefix) / 'share/jupyter/labextensions/jupyterlite-al-engine'
    if source.resolve() != target.resolve():
        shutil.copytree(source, target, dirs_exist_ok=True)
    if (target / load).read_bytes() != (source / load).read_bytes():
        raise ValueError('Installed labextension does not match the build.')
    print(f'Synced current labextension: {load}')


if __name__ == '__main__':
    main()
