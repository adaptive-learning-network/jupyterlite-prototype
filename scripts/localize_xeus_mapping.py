"""Bundle xeus' conda/PyPI aliases instead of fetching mutable metadata at startup."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UPSTREAM_URL = "https://raw.githubusercontent.com/prefix-dev/parselmouth/main/files/compressed_mapping.json"
MAPPING_SHA256 = "4c9e618d6e13f52b1fb0bda4d833565a05797f98c1d8973d2b7f7b96c9932a82"
MAPPING_REVISION = "offline-" + MAPPING_SHA256[:12]


def localize_xeus_mapping(output: Path, source: Path | None = None) -> int:
    source = source or ROOT / "app-assets/runtime/conda-pypi-mapping.json"
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != MAPPING_SHA256:
        raise ValueError("The bundled xeus package mapping does not match its reviewed SHA-256")
    mapping = json.loads(raw)
    if not isinstance(mapping, dict) or any(not isinstance(k, str) or v is not None and not isinstance(v, str)
                                            for k, v in mapping.items()):
        raise ValueError("Unexpected conda/PyPI mapping structure")
    # Keep the SDK's Response -> JSON behavior in window and worker contexts.
    # An inline Response avoids both an external request and base-URL assumptions
    # when the course is deployed under a GitHub Pages project subdirectory.
    payload = json.dumps(json.dumps(mapping, separators=(",", ":")))
    replacement = "Promise.resolve(new Response(" + payload + "))"
    changed = 0
    extension = output / "extensions/@jupyterlite/xeus-extension"
    for path in extension.rglob("*.js"):
        text = path.read_text(encoding="utf-8")
        if UPSTREAM_URL not in text:
            continue
        patched = text.replace("fetch(" + json.dumps(UPSTREAM_URL) + ")", replacement)
        patched = patched.replace("fetch('" + UPSTREAM_URL + "')", replacement)
        if UPSTREAM_URL in patched:
            raise ValueError("Unrecognized xeus metadata fetch: " + path.name)
        notice = "/*! Bundled prefix.dev conda/PyPI mapping; BSD-3-Clause. License: assets/runtime/parselmouth-LICENSE */\n"
        path.write_text(notice + patched, encoding="utf-8")
        changed += 1
    if extension.exists():
        # A new base directory also invalidates cached webpack child bundles.
        # Changing only the entry URL would leave their original cache keys intact.
        static = extension / "static"
        if static.is_dir():
            shutil.copytree(static, extension / MAPPING_REVISION / "static", dirs_exist_ok=True)
        target = output / "assets/runtime"
        target.mkdir(parents=True, exist_ok=True)
        for name in ("parselmouth-LICENSE", "conda-pypi-mapping.source.json"):
            shutil.copy2(ROOT / "app-assets/runtime" / name, target / name)
    print(f"Localized xeus package metadata in {changed} JavaScript bundles")
    return changed


def localized_xeus_load(load: str) -> str:
    load = load.replace("\\", "/")
    return load if load.startswith(MAPPING_REVISION + "/") else MAPPING_REVISION + "/" + load
