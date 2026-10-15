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

## Optional Unit 1 videos restored: 2026-10-15

The pinned upstream Unit 1 notebook contains three `YouTubeVideo` cells. A prior
localization removed their links but left the Additional Materials introduction.
The lesson now lists all three as optional videos with titles, publishers, and
viewing prompts. YouTube oEmbed returned each title and publisher on this date:

| Video | Publisher | Verified link |
| --- | --- | --- |
| Public Health Informatics: translating knowledge for health | Public Health Informatics Institute | https://www.youtube.com/watch?v=fLUygA8Hpfo |
| Introduction to Public Health Informatics | CDC | https://www.youtube.com/watch?v=Fzc3j8QG_Mw |
| Standards and Interoperability in Digital Health: Explained | TechChange | https://www.youtube.com/watch?v=KSEUh-wj7Y0 |

These specific links are allowlisted as optional enrichment, following the course
owner's clarification that YouTube is allowed. The notebook does not embed the
players or request YouTube content on load. The local explanations and visuals
remain available if a video is unavailable. Verification establishes resource
identity and endpoint availability, not playback within the CDC browser.

## Reflection coverage completed: 2026-10-15

The first response-storage update covered the practice-question library and nine
readings with local form responses. Nine other readings still used the generic
`Write your reasoning here` template. These were the Unit 1 slides and the Unit 2
slides, HIS context, case study, assignment 1, explore datasets, data quality,
compile/analyze, and analyze/visualize notebooks. Both scored Unit 1 and Unit 2
Python notebooks also had Markdown-only reflection prompts.

All eleven now use the shared text-entry and Record controls. All 18 source
readings have Python Jupyter kernel metadata and recordable response cells;
the reading index remains a navigation notebook. The build audit rejects the
old Markdown placeholders and missing reflection controls. Browser scenarios
exercise the Unit 2 slides and both scored notebooks, including recording and
restoring the slide reflection after a reload.
