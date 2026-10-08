#!/usr/bin/env python3
"""Download checksum-pinned, pure Python widget wheels for the local piplite index."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

from prepare_pyodide import download

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "pypi"
WHEELS = {
    "comm": ("0.2.3", "c615d91d75f7f04f095b30d1c1711babd43bdc6419c1be9886a85f2f4e489417"),
    "ipywidgets": ("8.1.7", "764f2602d25471c213919b8a1997df04bef869251db4ca8efba1b76b1bd9f7bb"),
    "jupyterlab_widgets": ("3.0.15", "d59023d7d7ef71400d51e6fee9a88867f6e65e10a4201605d2d7f3e8f012a31c"),
    "widgetsnbextension": ("4.0.14", "4875a9eaf72fbf5079dc372a51a9f268fc38d46f767cbf85c43a36da5cb9b575"),
}


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name, (version, digest) in WHEELS.items():
        request = urllib.request.Request(f"https://pypi.org/pypi/{name}/{version}/json", headers={"User-Agent": "JupyterLite-FETP-build"})
        with urllib.request.urlopen(request, timeout=30) as response:
            release = json.load(response)
        matches = [item for item in release["urls"] if item["filename"].endswith("-py3-none-any.whl") and item["digests"]["sha256"] == digest]
        if len(matches) != 1:
            raise ValueError(f"Pinned pure Python wheel not found: {name} {version}")
        wheel = matches[0]
        download(wheel["url"], OUT / wheel["filename"], digest)
    print(f"prepared {len(WHEELS)} checksum-pinned widget wheels in {OUT}")


if __name__ == "__main__":
    main()
