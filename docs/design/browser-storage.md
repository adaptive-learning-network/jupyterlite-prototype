# Browser storage and application assets

Updated 2026-10-22.

| Resource | Location | Update behavior |
| --- | --- | --- |
| Notebooks, datasets, slides, illustrations | JupyterLite contents drive | Supplied files come from the site; browser-saved learner copies take precedence. |
| Adaptive-learning engine | Bundled JupyterLab extension | Updated with the application. |
| Curriculum catalog and Python/R checks | Versioned `assets/adaptive-learning/<digest>/` site assets | Loaded directly by the extension, outside the contents drive. |
| Learner record and language preference | Browser `localStorage` | Existing keys and records are retained across this migration. |

The source catalog remains `catalog/informatics-unit-03.trig`. Generation writes
`app-assets/adaptive-learning/catalog.json` and `app-assets/adaptive-learning/checks/`.
After JupyterLite builds the course contents, `scripts/configure_site.py` copies
these resources to an asset directory whose name hashes the catalog and checks.
It writes that relative directory to the `alAssetsBaseUrl` page configuration.
Using the site's base URL supports GitHub Pages project paths and CDC GitLab Pages.

The extension fetches the catalog and checks from the same asset version. Checks
still run in the learner's Jupyter kernel. Notebook metadata keeps its logical
`checks/<name>` identifiers so older saved notebooks remain compatible. Browser
files with those names cannot override the application checks. A failed resource
request displays a retry message and does not add an observation.

This migration does not clear browser storage or remove a learner's saved files.
Fresh contents indexes no longer contain `al/` or `checks/`. A learner who edited
an old infrastructure file may still have a personal copy in browser storage;
that copy is no longer used by the extension.

Application assets remain inspectable through browser developer tools and direct
URLs. Their placement keeps infrastructure out of the learning workspace.

Validation includes the contents listing, direct asset loads, a missing-check
retry, Python/R check parity, and the existing adaptive scenarios for incomplete,
incorrect, repeated, and successful attempts, recommendations, exports, and reload.

## Local review and learner response persistence

The local VS Code preview is configured with `configure_site.py --course-review`.
On opening a supplied notebook, the extension compares its published version with
the last version seen in this browser. When a new course version is available, it
replaces the outdated review copy. Reviewer responses are disposable by request;
no backup copy is created. This setting is false in normal published builds.
The application asset manifest lists supplied notebook paths and versions;
personal notebooks outside that manifest are never replaced by review mode.

Reflection sections now provide **Record**. This explicitly saves every response
in that section under `reflections` in the same browser-local learner record as
observations and guidance. Entries contain the prompt, answer, and saved timestamp.
Stable section identifiers keep notebook and unit responses separate. Rerunning
the response cell restores recorded answers by matching the prompt text; changed
prompts do not silently receive an answer to a different question. Recording again
replaces that section's answers, including intentionally cleared fields.

Widgets use a Jupyter comm to the extension; only the extension writes browser
storage. A confirmation follows a successful storage write. A quota or storage
failure keeps the previous recorded version and reports that the new text was not
recorded. Unsaved edits remain drafts. Reflections are unscored and do not create
observations, capability evidence, or recommendations. Reset learner record also
clears recorded reflections. Browser storage is specific to the site and browser;
clearing it removes the record. **Export evidence** creates the RDF snapshot of
scored attempts and progress; it excludes reflection text. **Download reflections**
creates `recorded-reflections.txt` with all explicitly recorded section entries,
their question text, answers, and save times, including older sections retained
in storage. It does not mutate the record or include unsaved drafts. Edited
notebooks require a separate File-menu download. These files do not provide
automatic restoration; cross-device import remains future work. Reworded questions
still need stable IDs/version preservation, as recorded in audit finding C11.
Automatic replacement of learner notebooks remains disabled in published builds.
