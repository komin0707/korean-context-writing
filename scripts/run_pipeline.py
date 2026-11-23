#!/usr/bin/env python3
"""v3.0 writing pipeline: no personal-memory loading or mandatory review."""
from __future__ import annotations
import argparse
import datetime
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path
from revision_guard import check_revision

ROOT = Path(__file__).resolve().parents[1]
def load_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def context() -> str:
    return load_text(ROOT/"knowledge/voice-priority.md")

def fill(template: str, **values: str) -> str:
    for k,v in values.items():
        template=template.replace("{{"+k+"}}",v)
    if re.search(r"\{\{[A-Z_]+\}\}",template):
        raise ValueError("Unresolved prompt placeholder")
    return template

def run_command(command: str, prompt: str, timeout: int) -> str:
    args=shlex.split(command)
    if not args:
        raise ValueError("Empty model command")
    result=subprocess.run(args,input=prompt,text=True,capture_output=True,
                          encoding="utf-8",timeout=timeout,check=False)
    if result.returncode:
        raise RuntimeError("Model failed: "+result.stderr[-700:])
    if not result.stdout.strip():
        raise RuntimeError("Model returned empty output")
    return result.stdout.strip()

def parse_review(raw: str, draft: str) -> dict:
    fence=chr(96)*3
    raw=raw.strip()
    if raw.startswith(fence):
        raw=re.sub(r"^"+fence+r"(?:json)?\s*","",raw)
        raw=re.sub(r"\s*"+fence+r"$","",raw)
    item=json.loads(raw)
    if item.get("decision") not in {"accept","revise","needs_evidence"}:
        raise ValueError("Bad decision")
    issues=item.get("issues",[])
    if not isinstance(issues,list) or len(issues)>3:
        raise ValueError("At most three review issues")
    for x in issues:
        if not isinstance(x,dict) or not isinstance(x.get("span"),str) or not x["span"].strip() or x["span"] not in draft:
            raise ValueError("Issue span must be exact excerpt of the draft")
        if x.get("severity") not in {"major","minor"} or not x.get("problem") or not x.get("repair"):
            raise ValueError("Issue must have severity, problem, and repair")
    if item["decision"]=="revise" and not any(x["severity"]=="major" for x in issues):
        raise ValueError("Revision requires grounded major issue")
    if item["decision"]=="accept" and any(x["severity"]=="major" for x in issues):
        raise ValueError("Accept cannot include major issue")
    preserve=item.get("preserve",[])
    if not isinstance(preserve,list) or not all(isinstance(x,str) for x in preserve):
        raise ValueError("preserve must be list of strings")
    return item

def assemble_writer(task: str, sources: str, references: str = "") -> str:
    material=("# KOREAN WRITING SKILL\n"+load_text(ROOT/"SKILL.md")
            +"\n# VOICE PRIORITIES\n"+context()
            +"\n# OPTIONAL CRAFT LENSES\n"+load_text(ROOT/"knowledge/craft-lenses.md")
            +"\n"+fill(load_text(ROOT/"prompts/writer.md"),TASK=task,SOURCES=sources))
    if references.strip():
        material+="\n# REFERENCES SUPPLIED IN THIS REQUEST\n"+references
    return material

def assemble_polisher(task: str, sources: str, draft: str) -> str:
    return fill(load_text(ROOT/"prompts/polisher.md"),TASK=task,SOURCES=sources,DRAFT=draft)

def assemble_reviewer(task: str, sources: str, references: str, draft: str) -> str:
    prompt=fill(load_text(ROOT/"prompts/reviewer.md"),TASK=task,SOURCES=sources,DRAFT=draft)
    return prompt+("\n이번 작업에서 제공된 참고:\n"+references if references.strip() else "")

def assemble_reviser(task: str, sources: str, draft: str, review: dict) -> str:
    instructions={"issues":[{"span":x["span"],"repair":x["repair"]} for x in review.get("issues",[])],
                  "preserve":review.get("preserve",[])}
    return fill(load_text(ROOT/"prompts/reviser.md"),
                TASK=task,SOURCES=sources,DRAFT=draft,
                REVIEW=json.dumps(instructions,ensure_ascii=False,indent=2))

def main() -> int:
    parser=argparse.ArgumentParser(description="v3 draft or conservative polish")
    parser.add_argument("--task",required=True)
    parser.add_argument("--genre",default="일반",help="Metadata only; no memory lookup")
    parser.add_argument("--mode",choices=("draft","polish"),default="draft")
    parser.add_argument("--draft-file")
    parser.add_argument("--sources-file")
    parser.add_argument("--style-file",help="Explicit reference supplied for current task")
    parser.add_argument("--writer-cmd")
    parser.add_argument("--reviewer-cmd",help="Optional external reviewer")
    parser.add_argument("--prepare-only",action="store_true")
    parser.add_argument("--max-revisions",type=int,choices=(0,1),default=1)
    parser.add_argument("--timeout",type=int,default=180)
    parser.add_argument("--output",default="writing_output")
    args=parser.parse_args()
    if args.mode=="polish" and not args.draft_file:
        parser.error("--mode polish requires --draft-file")
    if not args.prepare_only and not args.writer_cmd:
        parser.error("Specify --writer-cmd or --prepare-only")
    sources=load_text(Path(args.sources_file)) if args.sources_file else "제공된 근거가 없다면 수치나 개인 경험을 창작하지 않는다."
    references=load_text(Path(args.style_file)) if args.style_file else ""
    original=load_text(Path(args.draft_file)) if args.mode=="polish" else ""
    out=Path(args.output).resolve()
    out.mkdir(parents=True,exist_ok=True)
    if args.mode=="polish":
        (out/"original.md").write_text(original,encoding="utf-8")
        prompt=assemble_polisher(args.task,sources,original)
        prompt_name="01_polisher_prompt.md"
    else:
        prompt=assemble_writer(args.task,sources,references)
        prompt_name="01_writer_prompt.md"
    (out/prompt_name).write_text(prompt,encoding="utf-8")
    if args.prepare_only:
        for number,name in [("02","reviewer"),("03","reviser")]:
            (out/(number+"_"+name+"_prompt_template.md")).write_text(
                load_text(ROOT/("prompts/"+name+".md")),encoding="utf-8")
        print("Prompts prepared; no LLM called:",out)
        return 0

    current=run_command(args.writer_cmd,prompt,args.timeout)
    (out/"draft_0.md").write_text(current+"\n",encoding="utf-8")
    status="UNREVIEWED_MODEL_OUTPUT"
    events=[]
    if args.mode=="polish":
        gate=check_revision(original,current)
        (out/"edit_guard_0.json").write_text(json.dumps(gate,ensure_ascii=False,indent=2),encoding="utf-8")
        if not gate["pass"]:
            current=original
            status="POLISH_ROLLED_BACK_PROTECTED_CONTENT"
            events.append({"step":"polish","failures":gate["failures"]})
    if args.reviewer_cmd and status=="UNREVIEWED_MODEL_OUTPUT":
        rp=assemble_reviewer(args.task,sources,references,current)
        (out/"review_prompt_0.md").write_text(rp,encoding="utf-8")
        raw=run_command(args.reviewer_cmd,rp,args.timeout)
        (out/"review_raw_0.txt").write_text(raw,encoding="utf-8")
        try:
            review=parse_review(raw,current)
        except (ValueError,json.JSONDecodeError) as exc:
            status="REVIEW_INVALID_NEEDS_HUMAN_CHECK"
            events.append({"step":"review","error":str(exc)})
        else:
            (out/"review_0.json").write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding="utf-8")
            decision=review["decision"]
            if decision=="accept":
                status="MODEL_REVIEW_PROVISIONAL"
            elif decision=="needs_evidence":
                status="REQUIRES_MORE_EVIDENCE"
            elif args.max_revisions==0:
                status="REVIEW_RECOMMENDS_REVISION"
            else:
                edit=assemble_reviser(args.task,sources,current,review)
                (out/"reviser_prompt_0.md").write_text(edit,encoding="utf-8")
                candidate=run_command(args.writer_cmd,edit,args.timeout)
                (out/"draft_1.md").write_text(candidate+"\n",encoding="utf-8")
                gate=check_revision(current,candidate)
                (out/"edit_guard_1.json").write_text(json.dumps(gate,ensure_ascii=False,indent=2),encoding="utf-8")
                if gate["pass"]:
                    current=candidate
                    status="MODEL_REVISED_UNVERIFIED"
                else:
                    status="REVISION_ROLLED_BACK_PROTECTED_CONTENT"
                    events.append({"step":"revision","failures":gate["failures"]})
    (out/"final_draft.md").write_text(current.rstrip()+"\n",encoding="utf-8")
    (out/"run_status.json").write_text(json.dumps({
        "status":status,"human_approved":False,"model_quality_verified":False,
        "mode":args.mode,"genre":args.genre,"personal_memory_used":False,
        "auto_examples_used":False,
        "timestamp":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "events":events},ensure_ascii=False,indent=2),encoding="utf-8")
    print("Final:",out/"final_draft.md")
    print("Status:",status,"(not human-approved)")
    return 0 if status in {"UNREVIEWED_MODEL_OUTPUT","MODEL_REVIEW_PROVISIONAL","MODEL_REVISED_UNVERIFIED"} else 2

if __name__=="__main__":
    sys.exit(main())
