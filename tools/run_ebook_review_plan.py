#!/usr/bin/env python3
"""Run WI-0019 without installing a package."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "src"))

from sammlungslotse.ebook_review_plan.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
