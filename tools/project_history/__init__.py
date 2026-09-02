"""Backward-compatible import path for Ragdoll Project History.

The production implementation lives under ``ragdoll.history``. This package is
kept so v0.7-era scripts/imports continue to work across the v1.0 production boundary.
"""

from ragdoll.history import *  # noqa: F401,F403
