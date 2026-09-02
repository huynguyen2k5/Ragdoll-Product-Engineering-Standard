#!/usr/bin/env python3
"""Score an OSS/tool candidate from a small JSON decision record.

Usage:
  python scripts/evaluate_candidate.py candidate.json

Each scored field is 0..5. Critical blockers override the numeric score.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

WEIGHTS = {
    "problem_fit": 25,
    "project_health": 15,
    "security_supply_chain": 15,
    "technical_compatibility": 15,
    "docs_tests": 10,
    "integration_cost": 10,
    "ecosystem_adoption": 5,
    "reversibility": 5,
}

BLOCKERS = ("license_blocker", "security_blocker", "compatibility_blocker")


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(2)


def main() -> None:
    if len(sys.argv) != 2:
        fail("expected path to candidate JSON")

    path = Path(sys.argv[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(str(exc))

    scores = data.get("scores", {})
    missing = [key for key in WEIGHTS if key not in scores]
    if missing:
        fail("missing score fields: " + ", ".join(missing))

    weighted = 0.0
    for key, weight in WEIGHTS.items():
        value = scores[key]
        if not isinstance(value, (int, float)) or not 0 <= value <= 5:
            fail(f"{key} must be a number from 0 to 5")
        # Integration cost is scored as fitness: 5 = low/easy cost, 0 = prohibitive.
        weighted += (value / 5.0) * weight

    blockers = [key for key in BLOCKERS if data.get(key) is True]
    if blockers:
        decision = "REJECT"
    elif weighted >= 80:
        decision = "ADOPT"
    elif weighted >= 65:
        decision = "TRIAL"
    elif weighted >= 50:
        decision = "WATCH"
    else:
        decision = "REJECT"

    result = {
        "candidate": data.get("candidate", "unnamed"),
        "weighted_score": round(weighted, 1),
        "decision_support": decision,
        "critical_blockers": blockers,
        "note": "Score supports judgment; explicit context and evidence still govern the decision.",
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
