#!/usr/bin/env python3
"""Validate per-model result sources without rebuilding the aggregate file."""

from __future__ import annotations

import sys

import build_results


def main() -> int:
    try:
        results = build_results.build(write=False)
    except build_results.ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"validated {len(results)} result files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
