"""Embed local teaching images as notebook attachments.

Browser-saved JupyterLite notebooks can outlive the virtual sibling assets from
the site build. Attachments keep each visual with the notebook copy.
"""

from __future__ import annotations

import base64
import re
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "content/exercises/assets"
IMAGE_REF = re.compile(r"\.\./assets/([a-z0-9-]+\.png)")
HTML_IMAGE = re.compile(r'<img src="(\.\./assets/[a-z0-9-]+\.png)" width="\d+" alt="([^"]+)">')


def embed_images(cell: dict) -> dict:
    if cell["cell_type"] != "markdown":
        return cell
    attachments = {}

    def replace(match: re.Match) -> str:
        name = match.group(1)
        image = ASSETS / name
        if not image.is_file():
            raise FileNotFoundError(image)
        attachments[name] = {"image/png": base64.b64encode(image.read_bytes()).decode("ascii")}
        return f"attachment:{name}"

    def convert_html(match: re.Match) -> str:
        return f"![{match.group(2)}]({match.group(1)})"

    cell["source"] = [IMAGE_REF.sub(replace, HTML_IMAGE.sub(convert_html, line)) for line in cell["source"]]
    if attachments:
        cell["attachments"] = attachments
    return cell
