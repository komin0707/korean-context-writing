#!/usr/bin/env python3
"""Conservative deterministic safety gate for an existing text being polished.

This is NOT an AI detector or a semantic-equivalence proof. It only checks
literal numeric tokens and double-quoted spans that should not quietly change.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

NUMERIC = re.compile(r"(?<![0-9])\d+(?:[.,]\d+)*(?![0-9])")
QUOTES = re.compile(r'“([^”\n]+)”|"([^"\n]+)"')

def protected_numbers(text: str) -> Counter[str]:
    return Counter(m.group().replace(",", "") for m in NUMERIC.finditer(text))

def quoted_spans(text: str) -> Counter[str]:
    return Counter(" ".join((m.group(1) or m.group(2)).split())
                   for m in QUOTES.finditer(text))

def check_revision(before: str, after: str) -> dict:
    n_before, n_after = protected_numbers(before), protected_numbers(after)
    q_before, q_after = quoted_spans(before), quoted_spans(after)
    missing_n = list((n_before - n_after).elements())
    added_n = list((n_after - n_before).elements())
    missing_q = list((q_before - q_after).elements())
    added_q = list((q_after - q_before).elements())
    failures = []
    if missing_n or added_n:
        failures.append("numbers_changed")
    if missing_q or added_q:
        failures.append("quoted_text_changed")
    return {
        "pass": not failures,
        "failures": failures,
        "removed_numbers": missing_n,
        "added_numbers": added_n,
        "removed_quoted_spans": missing_q,
        "added_quoted_spans": added_q,
        "limits": "Literal check only: semantic accuracy, hallucinations, tone and originality still require human or evidence-based review.",
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    args = parser.parse_args()
    result = check_revision(Path(args.before).read_text(encoding="utf-8"),
                            Path(args.after).read_text(encoding="utf-8"))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["pass"]:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
