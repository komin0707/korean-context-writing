#!/usr/bin/env python3
"""Structural package check, NOT creative-writing quality validation."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "SKILL.md", "README.md", "profiles/author-voice.yaml",
    "knowledge/context-map.md", "knowledge/creative-practice.md", "knowledge/form-selection.md", "knowledge/author-stance.md", "knowledge/empathy.md",
    "knowledge/korean-register.md", "knowledge/hooking.md", "knowledge/facts-and-evidence.md",
    "examples/README.md", "examples/approved.jsonl", "examples/partial.jsonl",
    "examples/rejected.jsonl", "tests/scenarios.jsonl", "tests/evaluation-rubric.md",
    "prompts/writer.md", "prompts/reviewer.md", "prompts/reviser.md",
    "prompts/WORK_START.md", "prompts/QUICK_START.md",
    "scripts/run_pipeline.py", "scripts/validate_package.py",
]


def main():
    for rel in REQUIRED:
        path = ROOT / rel
        assert path.is_file() and path.stat().st_size > 20, f"Missing/empty file: {rel}"
    assert (ROOT / "SKILL.md").read_text(encoding="utf-8").startswith("---\nname:")
    for rel in ("approved.jsonl", "partial.jsonl", "rejected.jsonl"):
        items = [json.loads(line) for line in (ROOT / "examples" / rel).read_text(encoding="utf-8").splitlines() if line.strip()]
        assert items, rel
    scenarios = [json.loads(line) for line in (ROOT / "tests/scenarios.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(scenarios) >= 10 and len({x["id"] for x in scenarios}) == len(scenarios)
    assert len(list((ROOT / "examples/rejected_articles").glob("*.md"))) >= 4
    print(f"PASS: package structure, JSONL, {len(scenarios)} scenario definitions; NOT an LLM quality test")


if __name__ == "__main__":
    main()
