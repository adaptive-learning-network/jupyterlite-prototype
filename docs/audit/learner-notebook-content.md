# Learner notebook content audit

Reviewed 2026-10-15.

The Unit 1 lesson section **1.2 Unit Slides** uses the local notebook link
`u01-n01-slides.ipynb`. That notebook contains local slide previews and a local PDF.
The generated notebook and the local server's supplied notebook both contain
this learner-facing wording. Neither contains “Source media”, “Original PDF link”,
or the earlier explanation of archival status and blocked Google Drive access.

The earlier remote PDF URL is retained for source review in the
[course link audit](../../../fetp-phi-course/docs/audit/form-links-audit.md).
CDC's `php/urlblock.php` URL is a network block-page wrapper around a destination,
not a course server to embed. The historical direct PDF destination is
[this Google Drive resource](https://drive.google.com/file/d/1fMH_U9sGqUJfT_cA85OC_SpUKJ_hqxyV/preview);
its content remains unverified and is not needed to read the lesson.

`scripts/add_course_references.py --check` scans every shipped notebook Markdown
cell for unreviewed external URLs, missing local images, and the known editorial
phrases above. The Unit 1 browser test also checks the rendered lesson and its local
slides link. These checks run in the site build.

The same audit found an illustration-production disclaimer in the introductory
comic cues of the scored Unit 1 and Unit 2 notebooks. That sentence was removed;
the case cues now describe only Laila's task. Illustration provenance belongs in
repository design notes and the references.

JupyterLite retains a modified notebook in browser storage even when the supplied
site copy changes. A screenshot of the earlier archival explanation therefore
needs a check of the saved copy as well as the source. Preserve learner work before
replacing that copy; rebuilding the site alone does not replace it. Source and
asset history belongs in this repository's audit and design documents.
