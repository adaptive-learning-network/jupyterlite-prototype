#!/usr/bin/env python3
"""Normalize Windows notebook paths in JupyterLite indexes and Pyodide.

Pyodide-kernel 0.8.6 inserts the notebook directory into a Python string
literal without escaping it. A directory like readings\\ucsf then contains an
invalid Unicode escape. Windows builds also put backslashes in the static
contents indexes, which prevents JupyterLite from saving nested notebooks.
Changed bundles get new filenames to bypass caches.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


OLD = r'os.chdir("${this._localPath}")'
NEW = r'os.chdir(${JSON.stringify(this._localPath.replaceAll("\\", "/"))})'
EXTENSION = "@jupyterlite/pyodide-kernel-extension"


def normalize_indexes(output: Path) -> int:
    """Use browser-style paths in every generated contents index."""
    changed = 0

    def normalize(node: object) -> object:
        nonlocal changed
        if isinstance(node, list):
            return [normalize(value) for value in node]
        if isinstance(node, dict):
            result = {}
            for key, value in node.items():
                if key == "path" and isinstance(value, str) and "\\" in value:
                    result[key] = value.replace("\\", "/")
                    changed += 1
                else:
                    result[key] = normalize(value)
            return result
        return node

    for path in (output / "api/contents").rglob("all.json"):
        source = path.read_text(encoding="utf-8")
        original = json.loads(source)
        normalized = normalize(original)
        if normalized != original:
            path.write_text(json.dumps(normalized, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return changed


def renamed(path: Path, source: str) -> Path:
    source = re.sub(r"\n//# sourceMappingURL=.*", "", source)
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]
    name = re.sub(r"\.[0-9a-f]{16}\.js$", f".{digest}.js", path.name)
    if name == path.name:
        raise ValueError(f"unrecognised bundle filename: {path.name}")
    target = path.with_name(name)
    target.write_text(source, encoding="utf-8")
    return target


def patch(output: Path) -> list[str]:
    extension = output / "extensions" / EXTENSION
    package_path = extension / "package.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    remote_path = extension / package["jupyterlab"]["_build"]["load"].replace("\\", "/")
    remote = remote_path.read_text(encoding="utf-8")
    match = re.search(r'\b393:"([0-9a-f]{16})"', remote)
    if not match:
        raise ValueError("Pyodide kernel chunk 393 not found; inspect the installed version")
    digest = match.group(1)
    chunk_path = remote_path.parent / f"393.{digest}.js"
    chunk = chunk_path.read_text(encoding="utf-8")
    names = re.findall(r'(?:coincident|comlink)\.worker\.[0-9a-f]{16}\.js', chunk)
    if len(names) != 2:
        raise ValueError("expected both Pyodide worker bundles")
    worker_sources = [
        (remote_path.parent / name, (remote_path.parent / name).read_text(encoding="utf-8"))
        for name in names
    ]
    sources = [chunk, *(source for _, source in worker_sources)]
    if all(OLD not in source for source in sources):
        if all(NEW in source for source in sources):
            return []
        raise ValueError("Pyodide startup expression changed; inspect before patching")
    if any(source.count(OLD) != 1 for source in sources):
        raise ValueError("Pyodide startup expression is inconsistent across bundles")

    changed = []
    for worker_path, source in worker_sources:
        new_path = renamed(worker_path, source.replace(OLD, NEW))
        chunk = chunk.replace(worker_path.name, new_path.name)
        changed.append(new_path.name)
    new_chunk = renamed(chunk_path, chunk.replace(OLD, NEW))
    remote = remote.replace(digest, new_chunk.name.split(".")[1])
    new_remote = renamed(remote_path, remote)
    package["jupyterlab"]["_build"]["load"] = f"static/{new_remote.name}"
    package_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")

    config_path = output / "jupyter-lite.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    extensions = config["jupyter-config-data"]["federated_extensions"]
    matching = [item for item in extensions if item["name"] == EXTENSION]
    if len(matching) != 1:
        raise ValueError("expected one Pyodide extension in JupyterLite config")
    matching[0]["load"] = f"static/{new_remote.name}"
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return changed + [new_chunk.name, new_remote.name]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("_output"))
    args = parser.parse_args()
    normalized = normalize_indexes(args.output)
    changed = patch(args.output)
    print(f"normalized {normalized} JupyterLite contents paths")
    print("patched Pyodide path handling: " + ", ".join(changed) if changed else "Pyodide path handling already patched")


if __name__ == "__main__":
    main()
