@AGENTS.md

## Claude-specific notes

- After changing the extension, rebuild the site (`jlpm build` then
  `jupyter lite build` and `python scripts/configure_site.py`, or simply
  `jlpm build:site`) before running Playwright. The tests run against `_output/`.
- When a Playwright test times out on a click, read the error for a blocking
  JupyterLab dialog (for example "File Load Error") before suspecting the
  feature under test.
- Never print or echo secret files (for example the workspace `.secrets/`
  folder). Pipe them directly into the command that needs them.
