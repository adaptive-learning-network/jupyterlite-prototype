#!/usr/bin/env python3
"""Prepare a small, checksum-verified Pyodide distribution for course notebooks.

The core archive and the wheels selected from its lockfile are copied into an
ignored build directory. JupyterLite's --pyodide option copies that directory
into the static site, so current Python exercises do not need a CDN at runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tarfile
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
VERSION = "314.0.6"
CORE_NAME = f"pyodide-core-{VERSION}.tar.bz2"
CORE_SHA256 = "1016c31e39ce3764d9a418cbb491a392c802c1b86ccc1367f009f5c59bf8f5fd"
CORE_URL = f"https://github.com/pyodide/pyodide/releases/download/{VERSION}/{CORE_NAME}"
WHEEL_URL = f"https://cdn.jsdelivr.net/pyodide/v{VERSION}/full"
REQUIRED_PACKAGES = ("micropip", "ipython", "jedi", "pandas")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, path: Path, expected_sha256: str) -> None:
    if path.is_file() and sha256(path) == expected_sha256:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".part")
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "JupyterLite-FETP-build"})
        with urllib.request.urlopen(request, timeout=120) as source, temporary.open("wb") as target:
            shutil.copyfileobj(source, target)
        actual = sha256(temporary)
        if actual != expected_sha256:
            raise ValueError(f"SHA-256 mismatch for {path.name}: {actual}")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def extract_core(archive: Path, output: Path) -> None:
    with tarfile.open(archive, "r:bz2") as bundle:
        for member in bundle:
            name = member.name.removeprefix("pyodide/")
            if not member.isfile() or Path(name).name != name:
                continue
            source = bundle.extractfile(member)
            if source is None:
                raise ValueError(f"Cannot read {member.name}")
            with source, (output / name).open("wb") as target:
                shutil.copyfileobj(source, target)


def required_wheels(lock: dict) -> list[tuple[str, str]]:
    packages = lock["packages"]
    pending = list(REQUIRED_PACKAGES)
    selected = set()
    while pending:
        name = pending.pop().replace("_", "-").lower()
        if name in selected:
            continue
        selected.add(name)
        pending.extend(packages[name]["depends"])
    wheels = []
    for name in sorted(selected):
        package = packages[name]
        filename = package["file_name"]
        if Path(filename).name != filename or not filename.endswith(".whl"):
            raise ValueError(f"Unexpected wheel filename: {filename}")
        wheels.append((filename, package["sha256"]))
    return wheels


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / ".tools/pyodide")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    distribution = output / "pyodide"
    distribution.mkdir(parents=True, exist_ok=True)
    archive = output.parent / CORE_NAME
    download(CORE_URL, archive, CORE_SHA256)
    extract_core(archive, distribution)
    lock = json.loads((distribution / "pyodide-lock.json").read_text(encoding="utf-8"))
    release = json.loads((distribution / "package.json").read_text(encoding="utf-8"))
    if release["version"] != VERSION:
        raise ValueError("Pyodide distribution version does not match the pinned runtime")
    wheels = required_wheels(lock)
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(download, f"{WHEEL_URL}/{name}", distribution / name, digest) for name, digest in wheels]
        for future in futures:
            future.result()
    total = sum(path.stat().st_size for path in distribution.iterdir() if path.is_file())
    print(f"Pyodide {VERSION}: {len(wheels)} pinned wheels; {total / 1024 / 1024:.1f} MiB in {distribution}")


if __name__ == "__main__":
    main()
