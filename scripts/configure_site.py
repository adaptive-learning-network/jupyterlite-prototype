#!/usr/bin/env python3
"""Post-build site configuration for _output/.

1. Copies static pages from site/ (oidc-callback.html) to the site root.
2. If lite/oidc.json exists, adds it to jupyter-lite.json as `alOidc`, which
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
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOWED = {"issuer", "clientId", "scope", "redirectUri", "label"}


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
    args = parser.parse_args()

    for page in sorted((ROOT / "site").glob("*.html")):
        shutil.copy2(page, args.output / page.name)
        print(f"copied site/{page.name}")

    oidc = load_oidc(args.oidc)
    if oidc is None:
        print("no lite/oidc.json: sign-in disabled")
        return 0
    for config_path in (args.output / "jupyter-lite.json", args.output / "lab/jupyter-lite.json"):
        if not config_path.exists():
            continue
        config = json.loads(config_path.read_text())
        config.setdefault("jupyter-config-data", {})["alOidc"] = oidc
        config_path.write_text(json.dumps(config, indent=2) + "\n")
    print(f"sign-in enabled for issuer {oidc['issuer']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
