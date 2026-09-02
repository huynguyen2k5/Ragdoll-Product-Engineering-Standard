"""Compatibility wrapper for :mod:`ragdoll.history.cli`."""
from ragdoll.history.cli import main, parser

__all__ = ["main", "parser"]

if __name__ == "__main__":
    raise SystemExit(main())
