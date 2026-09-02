#!/usr/bin/env python3
"""CLI wrapper for :mod:`ragdoll.context_generation`."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ragdoll.context_generation import main


if __name__ == "__main__":
    raise SystemExit(main())
