#!/usr/bin/env python3
"""Post-build site configuration for _output/.

1. Copies static pages from site/ (oidc-callback.html) to the site root.
2. Publishes the generated catalog and checks as versioned application assets,
   outside the learner contents drive, and configures `alAssetsBaseUrl`.
3. If lite/oidc.json exists, adds it to jupyter-lite.json as `alOidc`, which
   enables "Link organisation sign-in" in the learning panel.

lite/oidc.json holds PUBLIC values only. This is a public client (PKCE); a static
site cannot keep a secret, so any secret-looking key is rejected:

  {
    "issuer": "https://login.example.org/realms/fetp",
    "clientId": "jupyterlite-al-engine",
    "label": "Organisation sign-in"
  }

Register <site>/oidc-callback.html as the redirect URI with the provider, and
allow the site origin for CORS on the token endpoint (SPA / public client).

Usage: python scripts/configure_site.py [--oidc lite/oidc.json] [--output _output]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

from localize_xeus_mapping import localize_xeus_mapping, localized_xeus_load

ROOT = Path(__file__).resolve().parent.parent
ALLOWED = {"issuer", "clientId", "scope", "redirectUri", "label"}


def publish_adaptive_assets(output: Path) -> str:
    if any((output / "files" / folder).exists() for folder in ("al", "checks")):
        raise ValueError("Rebuild the site without adaptive resources in the learner contents drive")
    source = ROOT / "app-assets/adaptive-learning"
    files = [source / "catalog.json", *sorted((source / "checks").glob("*.py")),
             *sorted((source / "checks").glob("*.R"))]
    if not (source / "catalog.json").is_file() or not list((source / "checks").glob("*.py")):
        raise ValueError("Generate the adaptive-learning catalog and checks before building the site")
    for notebook in sorted((ROOT / ".course-content").rglob("*.ipynb")):
        document = json.loads(notebook.read_text(encoding="utf-8"))
        language = document["metadata"].get("kernelspec", {}).get("language", "").lower()
        extension = {"python": "py", "r": "R"}.get(language)
        for cell in document["cells"]:
            check = cell.get("metadata", {}).get("al", {}).get("check")
            if check and (not extension or not (source / f"{check}.{extension}").is_file()):
                raise ValueError(f"Missing application check for {notebook.name}: {check}")
    digest = hashlib.sha256()
    for path in files:
        digest.update(path.relative_to(source).as_posix().encode("utf-8") + b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    versions = {path.relative_to(ROOT / ".course-content").as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted((ROOT / ".course-content").rglob("*.ipynb"))}
    manifest = (json.dumps(versions, sort_keys=True, indent=2) + "\n").encode("utf-8")
    digest.update(b"notebooks.json\0" + hashlib.sha256(manifest).digest())
    relative = f"assets/adaptive-learning/{digest.hexdigest()[:20]}"
    for path in files:
        target = output / relative / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    (output / relative / "notebooks.json").write_bytes(manifest)
    print(f"published {len(files) + 1} adaptive-learning application assets to {relative}")
    return relative + "/"


def load_oidc(path: Path) -> dict | None:
    if not path.exists():
        return None
    config = json.loads(path.read_text())
    secretish = [k for k in config if "secret" in k.lower() or "password" in k.lower()]
    if secretish:
        raise SystemExit(f"{path}: remove {secretish}; a static site is a public client and cannot keep secrets")
    unknown = sorted(set(config) - ALLOWED)
    if unknown:
        raise SystemExit(f"{path}: unsupported keys {unknown}; allowed: {sorted(ALLOWED)}")
    if not str(config.get("issuer", "")).startswith("https://") or not config.get("clientId"):
        raise SystemExit(f"{path}: needs an https issuer and a clientId")
    scope = config.get("scope", "openid").split()
    if "openid" not in scope or {"email", "profile"} & set(scope):
        raise SystemExit(f"{path}: scope must include openid and must not request email or profile")
    return config


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--oidc", type=Path, default=ROOT / "lite/oidc.json")
    parser.add_argument("--output", type=Path, default=ROOT / "_output")
    parser.add_argument("--course-review", action="store_true",
                        help="local reviewer mode: replace outdated supplied notebook copies on open without retaining review responses")
    args = parser.parse_args()

    localize_xeus_mapping(args.output)

    for page in sorted((ROOT / "site").glob("*.html")):
        shutil.copy2(page, args.output / page.name)
        print(f"copied site/{page.name}")

    assets_base = publish_adaptive_assets(args.output)
    oidc = load_oidc(args.oidc)
    for config_path in (args.output / "jupyter-lite.json", *sorted(args.output.glob("*/jupyter-lite.json"))):
        if not config_path.exists():
            continue
        config = json.loads(config_path.read_text())
        data = config.setdefault("jupyter-config-data", {})
        # JupyterLab's Windows build metadata uses filesystem separators.
        # Extension loaders consume URLs, including for the current local build.
        for extension in data.get("federated_extensions", []):
            if isinstance(extension.get("load"), str) and "\\" in extension["load"]:
                extension["load"] = "/".join(part for part in extension["load"].replace("\\", "/").split("/") if part)
            if extension.get("name") == "@jupyterlite/xeus-extension":
                extension["load"] = localized_xeus_load(extension["load"])
        # Python-only review builds omit xeus environments. Do not initialize
        # their unused frontend (which fetches an optional remote package map).
        # Builds containing xeus kernels retain the existing R runtime.
        if args.course_review and not (args.output / "xeus/kernels.json").exists():
            data["federated_extensions"] = [extension for extension in data.get("federated_extensions", [])
                                            if extension.get("name") != "@jupyterlite/xeus-extension"]
        # These short teaching notebooks contain collapsible media and live widgets.
        # Keep every cell attached: full windowing can leave a blank viewport after
        # scrolling past hidden inputs or closed slide sections.
        data.setdefault("settingsOverrides", {}).setdefault(
            "@jupyterlab/notebook-extension:tracker", {})["windowingMode"] = "none"
        data["alAssetsBaseUrl"] = assets_base
        data["alCourseReviewMode"] = args.course_review
        if oidc is not None:
            data["alOidc"] = oidc
        else:
            data.pop("alOidc", None)
        config_path.write_text(json.dumps(config, indent=2) + "\n")
    print(f"sign-in enabled for issuer {oidc['issuer']}" if oidc else "no lite/oidc.json: sign-in disabled")
    return 0


if __name__ == "__main__":
    sys.exit(main())
