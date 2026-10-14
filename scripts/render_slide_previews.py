"""Render committed course PDFs as small, browser-friendly slide previews.

Run after converting the supplied Version 2 PowerPoint decks to PDF. The PDF
is the full-size source for each preview; no slide text is rewritten here.
"""

from pathlib import Path

import pymupdf


ASSETS = Path(__file__).resolve().parents[1] / "content/readings/ucsf/assets"
for unit in (1, 2):
    pdf = ASSETS / f"unit-{unit}-version-2-slides.pdf"
    document = pymupdf.open(pdf)
    target = ASSETS / "slide-previews"
    target.mkdir(exist_ok=True)
    for number, page in enumerate(document, 1):
        scale = 880 / page.rect.width
        pixmap = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False)
        (target / f"unit-{unit}-{number:03d}.jpg").write_bytes(pixmap.tobytes("jpeg", jpg_quality=76))
    print(f"Unit {unit}: {len(document)} pages rendered")
