"""Ontology-driven adaptive-learning engine for JupyterLite (prebuilt JupyterLab extension)."""

try:
    from ._version import __version__
except ImportError:  # pragma: no cover - source checkout without a build
    __version__ = "dev"


def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": "jupyterlite-al-engine"}]
