# Browser storage and application assets

Updated 2026-10-15.

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

Production must preserve learner answers and reflection notes independently of
course revisions and Jupyter kernel restarts. The existing learner record persists
observations and guidance, not the text entered in reflection widgets. Those
widgets currently hold text for the live Jupyter kernel session. Durable response
storage, restore behavior, and export need implementation and validation before
the course is considered ready for production learners. Automatic replacement of
learner notebooks remains disabled in the published prototype.
