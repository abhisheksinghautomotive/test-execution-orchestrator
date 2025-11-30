#!/usr/bin/env python3
import sys
from pathlib import Path
from typing import Optional
import defusedxml.ElementTree as ET

COVERAGE_XML = Path("coverage.xml")
THRESHOLD = float(sys.argv[1]) if len(sys.argv) > 1 else 80.0


def _safe_int(value: Optional[str]) -> Optional[int]:
    return int(value) if value is not None else None


def compute_coverage(path: Path) -> float:
    tree = ET.parse(str(path))
    root = tree.getroot()

    line_rate_str = root.get("line-rate")
    if line_rate_str is not None:
        try:
            return float(line_rate_str) * 100.0
        except ValueError:
            pass

    totals = root.find(".//totals")
    if totals is not None:
        covered = _safe_int(totals.get("covered"))
        total_n = _safe_int(totals.get("num_statements"))
        if covered is not None and total_n and total_n > 0:
            return (covered / total_n) * 100.0

    raise RuntimeError("Unable to determine coverage percentage from coverage.xml")


def main() -> int:
    if not COVERAGE_XML.exists():
        print(
            "error: coverage.xml not found. Run pytest with --cov first.",
            file=sys.stderr,
        )
        return 2

    try:
        pct = compute_coverage(COVERAGE_XML)
    except Exception as e:
        print(f"error: failed to parse coverage.xml: {e}", file=sys.stderr)
        return 3

    print(f"Total coverage: {pct:.2f}% (threshold: {THRESHOLD}%)")
    if pct + 1e-9 < THRESHOLD:
        print("Coverage check FAILED", file=sys.stderr)
        return 1

    print("Coverage check PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
