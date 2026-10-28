# Field demonstration slides

- [Revised PowerPoint](field-demo-revised.pptx)
- [Revised PDF copy](field-demo-revised.pdf)
- [Presenter notes](field-demo-speaker-notes.md)
- [Presentation plan](field-demo-presentation-plan.md)

The 16-slide presentation introduces JupyterLite, computational narratives,
and this course's adaptive-learning support for field epidemiologists. The
walkthrough shows Notebook 00, course contents, the Run toolbar, classification
controls, feedback, and a recorded reflection. A dedicated Learning panel slide
shows suggested activities, current exercise support, and recorded progress.
Three slides shift the audience into the producer role: epidemiologists as
course authors, a typical AI-assisted improvement workflow, and human review
of a contribution before release. Allow approximately 25 minutes plus discussion.
Links open the public course and
U03-N06 directly. All teaching images are embedded, so the slide presentation
and its recorded examples do not depend on live image requests.

The screenshots show the published prototype on 23 October 2026 with invented
data and demonstration responses. The practice/different-case distinction is
specific to U03-N06. The presentation makes no claim of validated learning
effectiveness or workplace proficiency.

## Slide 2 and slide 4 revision: 27 October 2026

Slide 2 now defines an explicitly invented suspected-measles reporting scenario
over two consecutive weeks and asks which district has the largest increase in
reported cases. Slide 4 uses those same Kambia counts and week labels to calculate
the increase from 2 to 7. The comparison does not rank districts' epidemiologic
priority. The original Unit 1 numeric fixture does not specify a disease, so the
speaker notes identify the presentation's added scenario assumption.

The revised documents use a new filename because the original PowerPoint was
open and locked during this revision. The original files remain available as
`field-demo.pptx` and `field-demo.pdf`.

## Updating the presentation

Edit slide content, layout, and speaker notes in `build_field_demo.py`. Screenshots
live in `assets/`. From the repository root on Windows with Microsoft PowerPoint
installed:

```powershell
.venv/Scripts/python.exe docs/presentations/build_field_demo.py
powershell -NoProfile -File docs/presentations/export_field_demo.ps1 -OutputStem field-demo-revised
```

The Python script prepares a layout model under the ignored `.tools/` directory.
The PowerShell script uses PowerPoint's document object model to construct native
editable text and tables, embed images, add notes and hyperlinks, and export the
PowerPoint and PDF. The metadata cleanup helper uses the existing PyMuPDF
dependency to set generic course metadata. The exporter opens the new document without a presentation window and
closes only the document it creates. Slide renderings also stay under `.tools/`.

Rebuilding overwrites the supplied PowerPoint/PDF and the separate notes file.
Keep manual edits in a differently named copy, or update the source before
rebuilding. Review all slides after changes, especially screenshot legibility.
