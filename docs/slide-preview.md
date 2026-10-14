# Local slide previews

Reviewed 2026-10-14.

The Unit 1 and Unit 2 slide readings contain expandable page ranges with a
preview of every visible PDF page. Selecting **Open this PDF page** opens the
full PDF at that page; **Open the full slide PDF** opens its browser page
controls. The preview images and PDFs are served from this JupyterLite site,
so the learner does not need the Google Slides or Drive viewer.

| Slide reading | Supplied PowerPoint | PDF pages | PowerPoint slides |
| --- | --- | ---: | ---: |
| `u01-n01-slides.ipynb` | `Unit 1 v2_ Intro to Informatics for FETP.pptx` | 30 | 31 |
| `u02-n01-slides.ipynb` | `Unit 2_v2_ Detection and Diagonosis.pptx` | 112 | 115 |

The PDFs were exported from the supplied *FETP Informatics Course.zip* in
Downloads using PowerPoint on Windows. The exported PDFs omit hidden
PowerPoint slides. Page numbers in the previews refer to the PDFs. These are
Version 2 local course decks and have not been verified as identical to the
files linked by the UCSF JupyterBook. The original UCSF links remain in the
reading notebooks for source attribution.

To regenerate from the supplied extracted archive on Windows:

```powershell
./scripts/convert_source_slides.ps1 -SourceDirectory 'C:\path\to\FETP Informatics Course'
uv run --no-project --python 3.12 --with pymupdf python scripts/render_slide_previews.py
python scripts/import_ucsf_readings.py --reuse-local
```

The last command rebuilds the slide gallery cells and reading navigation from
the local notebook text. Review slide page counts in
`scripts/import_ucsf_readings.py` if the decks change. The checked-in PDFs and
JPEG previews are the build inputs; the published site does not run PowerPoint.
