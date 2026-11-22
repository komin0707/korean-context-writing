#!/usr/bin/env python3
"""Model-agnostic writing loop. Standard library only.

The runner DOES NOT supply an LLM. Configure command-line model clients that
accept a prompt on stdin and print an answer to stdout, or use --prepare-only.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path
from feedback_memory import context_text, canonical_genre, pick_entries

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "prompts"
KNOWLEDGE = ROOT / "knowledge"


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_examples() -> str:
    blocks = []
    for name in ("approved", "partial", "rejected"):
        path = ROOT / "examples" / f"{name}.jsonl"
        items = [json.loads(line) for line in load_text(path).splitlines() if line.strip()]
        blocks.append(f"[{name.upper()} — approval status MUST be respected]\n" +
                      "\n".join(json.dumps(item, ensure_ascii=False) for item in items))
    return "\n\n".join(blocks)


def context() -> str:
    return load_text(KNOWLEDGE / "editorial-voice.md") + "\n\n" + load_text(KNOWLEDGE / "creative-practice.md")


def approved_writer_context(genre: str, topic: str) -> str:
    approved = [x for x in pick_entries(genre, topic, limit_per_status=4)
                if x.get("status") == "approved"]
    if not approved:
        return "화자 프로필과 긍정형 실행 지침을 바탕으로 고유한 관점을 형성한다."
    return "\n".join(
        f"사용자가 승인한 문체 (소재: {x.get('topic', '')}): {x['quote']}"
        for x in approved
    )


def fill(template: str, **values: str) -> str:
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    if re.search(r"\{\{[A-Z_]+\}\}", template):
        raise ValueError("Unresolved prompt placeholders")
    return template


def run_command(command: str, prompt: str, timeout: int) -> str:
    argv = shlex.split(command)
    if not argv:
        raise ValueError("empty model command")
    result = subprocess.run(argv, input=prompt, capture_output=True, text=True,
                            encoding="utf-8", timeout=timeout, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Model command returned {result.returncode}: {result.stderr[-700:]}")
    if not result.stdout.strip():
        raise RuntimeError("Model command returned empty stdout")
    return result.stdout.strip()


def parse_review(raw: str, draft: str) -> dict:
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    item = json.loads(raw)
    if item.get("decision") not in {"revise", "provisional", "needs_evidence"}:
        raise ValueError("review.decision must be revise/provisional/needs_evidence")
    expected = {"context", "stance", "voice", "empathy", "hook", "truthfulness"}
    scores = item.get("scores", {})
    if set(scores) != expected or any(type(scores[x]) is not int or scores[x] not in range(4) for x in expected):
        raise ValueError("review.scores must contain six integer 0-3 ratings")
    issues = item.get("issues")
    if not isinstance(issues, list) or not issues:
        raise ValueError("review must include at least one evidence-based issue")
    for issue in issues:
        span = issue.get("span", "").strip()
        if not span or span not in draft:
            raise ValueError(f"review span is not in draft: {span[:70]!r}")
        if not issue.get("problem") or not issue.get("repair"):
            raise ValueError("review issue missing problem/repair")
    if scores["truthfulness"] == 0:
        item["decision"] = "revise"
    if any(v == 0 for v in scores.values()):
        item["decision"] = "revise"
    if any(scores[k] <= 2 for k in ("voice", "empathy", "stance", "hook")):
        item["decision"] = "revise"
    if any(issue.get("severity") == "major" for issue in issues):
        item["decision"] = "revise"
    return item


def assemble_writer(task: str, sources: str, references: str) -> str:
    template = load_text(PROMPTS / "writer.md")
    return ("# KOREAN WRITING SKILL\n" + load_text(ROOT / "SKILL.md") + "\n\n" +
            "# KNOWLEDGE\n" + context() + "\n\n" +
            fill(template, TASK=task, SOURCES=sources, STYLE_REFERENCES=references,
                 AUTHOR_PROFILE=load_text(ROOT / "profiles" / "author-voice.yaml")))


def assemble_reviewer(task: str, sources: str, references: str, draft: str) -> str:
    return fill(load_text(PROMPTS / "reviewer.md"), TASK=task, SOURCES=sources,
                STYLE_REFERENCES=references, DRAFT=draft)


def assemble_reviser(task: str, sources: str, draft: str, review: dict) -> str:
    actions = {
        "direction": review.get("revision_priority", ""),
        "improvements": [x.get("repair", "") for x in review.get("issues", [])],
        "preserve": review.get("what_to_preserve", []),
    }
    return ("# KOREAN WRITING SKILL\n" + load_text(ROOT / "SKILL.md") + "\n\n" +
            fill(load_text(PROMPTS / "reviser.md"), TASK=task, SOURCES=sources,
                 DRAFT=draft, REVIEW=json.dumps(actions, ensure_ascii=False, indent=2)))


def main() -> int:
    parser = argparse.ArgumentParser(description="Korean-writing loop: prepare prompts or run configured external LLM CLIs")
    parser.add_argument("--task", required=True, help="Writing request")
    parser.add_argument("--genre", required=True, help="Genre for durable-feedback retrieval: e.g. 건강정보 / 이슈논평 / 감정경험")
    parser.add_argument("--sources-file", help="UTF-8 source notes text path")
    parser.add_argument("--writer-cmd", help="LLM CLI command, prompt via stdin")
    parser.add_argument("--reviewer-cmd", help="Independent LLM CLI command, prompt via stdin")
    parser.add_argument("--prepare-only", action="store_true", help="No model calls; generate ready-to-use stage prompts")
    parser.add_argument("--max-revisions", type=int, default=2, choices=(0, 1, 2))
    parser.add_argument("--timeout", type=int, default=180, help="Per command timeout in seconds")
    parser.add_argument("--output", default="writing_output", help="Output directory")
    args = parser.parse_args()

    if not args.prepare_only and (not args.writer_cmd or not args.reviewer_cmd):
        parser.error("Set --prepare-only or provide BOTH --writer-cmd and --reviewer-cmd")

    sources = load_text(Path(args.sources_file)) if args.sources_file else "확인된 근거와 화자의 해석을 구분하고 검증 범위를 정확하게 전한다."
    refs = approved_writer_context(args.genre, args.task)
    reviewer_refs = refs
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "00_selected_memory.md").write_text(refs, encoding="utf-8")
    (out / "00_reviewer_memory.md").write_text(reviewer_refs, encoding="utf-8")
    writer_prompt = assemble_writer(args.task, sources, refs)
    (out / "01_writer_prompt.md").write_text(writer_prompt, encoding="utf-8")

    if args.prepare_only:
        (out / "02_reviewer_prompt_template.md").write_text(load_text(PROMPTS / "reviewer.md"), encoding="utf-8")
        (out / "03_reviser_prompt_template.md").write_text(load_text(PROMPTS / "reviser.md"), encoding="utf-8")
        print("Prompt bundle saved:", out)
        print("No LLM called; no quality claim is possible.")
        return 0

    writer = run_command(args.writer_cmd, writer_prompt, args.timeout)
    (out / "draft_0.md").write_text(writer + "\n", encoding="utf-8")
    outcome = "MODEL_REVIEW_PROVISIONAL"
    run_log = []
    for attempt in range(args.max_revisions + 1):
        rp = assemble_reviewer(args.task, sources, reviewer_refs, writer)
        (out / f"review_prompt_{attempt}.md").write_text(rp, encoding="utf-8")
        raw = run_command(args.reviewer_cmd, rp, args.timeout)
        (out / f"review_raw_{attempt}.txt").write_text(raw, encoding="utf-8")
        try:
            review = parse_review(raw, writer)
        except (ValueError, json.JSONDecodeError) as exc:
            outcome = "REVIEW_INVALID_NEEDS_HUMAN_CHECK"
            run_log.append({"attempt": attempt, "error": str(exc)})
            break
        (out / f"review_{attempt}.json").write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")
        run_log.append({"attempt": attempt, "decision": review["decision"], "scores": review["scores"]})
        if review["decision"] == "provisional":
            break
        if review["decision"] == "needs_evidence":
            outcome = "REQUIRES_MORE_EVIDENCE"
            break
        if attempt == args.max_revisions:
            outcome = "REVIEW_FAILED_MAX_REVISIONS"
            break
        revision_prompt = assemble_reviser(args.task, sources, writer, review)
        (out / f"reviser_prompt_{attempt}.md").write_text(revision_prompt, encoding="utf-8")
        writer = run_command(args.writer_cmd, revision_prompt, args.timeout)
        (out / f"draft_{attempt + 1}.md").write_text(writer + "\n", encoding="utf-8")

    (out / "final_draft.md").write_text(writer + "\n", encoding="utf-8")
    (out / "run_status.json").write_text(json.dumps({
        "status": outcome,
        "human_approved": False,
        "genre": canonical_genre(args.genre),
        "persistent_memory": str(ROOT / "memory" / "feedback.jsonl"),
        "independence_note": "Two separately invoked CLIs; separate models/sessions not technically verifiable by this script.",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "attempts": run_log,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Draft:", out / "final_draft.md")
    print("Review status:", outcome, "(NOT human-approved)")
    return 0 if outcome == "MODEL_REVIEW_PROVISIONAL" else 2


if __name__ == "__main__":
    sys.exit(main())
