#!/usr/bin/env python3
"""Check v3 package structure and test scenarios, not generated prose quality."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REQUIRED=[
    "SKILL.md","README.md","RELEASE_NOTES.md","CLAUDE_PROJECT_INSTRUCTIONS.md",
    "knowledge/voice-priority.md","knowledge/craft-lenses.md",
    "prompts/writer.md","prompts/polisher.md","prompts/reviewer.md","prompts/reviser.md",
    "prompts/WORK_START.md","prompts/QUICK_START.md",
    "scripts/run_pipeline.py","scripts/revision_guard.py","scripts/validate_package.py",
    "docs/borrowed-design.md","lexicon/verified.jsonl","lexicon/README.md","research/collection-notes.md","research/candidates_index.jsonl","research/sources.json","scripts/select_slang.py","scripts/refresh_slang_candidates.py","tests/scenarios.jsonl","tests/evaluation-rubric.md"
]
def main():
    for rel in REQUIRED:
        path=ROOT/rel
        assert path.is_file() and path.stat().st_size>20,f"Missing/empty {rel}"
    skill=(ROOT/"SKILL.md").read_text(encoding="utf-8")
    assert skill.startswith("---\nname:") and 'version: "3.1.0-preview"' in skill
    scenarios=[json.loads(line) for line in (ROOT/"tests/scenarios.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(scenarios)>=10 and len({x["id"] for x in scenarios})==len(scenarios)
    for rel in ("SETUP_PERSISTENCE.md","memory/feedback.jsonl","scripts/feedback_memory.py","profiles/author-voice.yaml"):
        assert not (ROOT/rel).exists(),f"Personal memory still present: {rel}"
    print(f"PASS v3: {len(REQUIRED)} required files, {len(scenarios)} scenarios, no personal-memory modules; NOT an LLM writing quality test")
if __name__=="__main__":
    main()
