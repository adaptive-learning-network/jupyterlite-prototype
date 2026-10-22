# Bundled runtime metadata

`conda-pypi-mapping.json` contains prefix.dev's conda-to-PyPI package aliases,
pinned to the upstream revision and SHA-256 in `conda-pypi-mapping.source.json`.
The upstream BSD-3-Clause license is retained in `parselmouth-LICENSE`.

The xeus frontend otherwise fetches the mutable mapping during application
startup, including when the learner uses Python. `scripts/configure_site.py`
calls `localize_xeus_mapping.py` to embed the reviewed mapping as an in-memory
Fetch `Response` in the installed frontend bundles. No metadata server is
needed at runtime. This preserves the SDK's alias lookup and the existing R
runtime rather than disabling its initialization or weakening the offline test.
The configured frontend loads from a versioned base directory so returning
browsers also fetch the patched child bundles instead of cached upstream copies.
The static directory is moved into that versioned location rather than copied;
stale source maps for rewritten bundles are omitted to keep deployment artifacts small.

The source revision and checksum must be reviewed together when this data is
updated. Changed data fails the build until its pinned checksum is updated.
The published site also includes the license and source metadata under
`assets/runtime/`, outside the learner file browser.
