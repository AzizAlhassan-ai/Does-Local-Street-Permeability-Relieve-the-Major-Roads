"""Shared helpers for the local-permeability / arterial-traffic study.

Import from stage scripts as:

    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # -> code/
    from lib import cfg, paths, provenance, validate

Note: `code/` is deliberately NOT a package. A top-level package named `code`
would shadow Python's stdlib `code` module.
"""
