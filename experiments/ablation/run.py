#!/usr/bin/env python3
"""Paired, controlled prompts for comparing existing Korean-writing configurations.

Read-only to the original skill. Offline preparation is the default.
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
from run_pipeline import assemble_writer, approved_writer_context

def git_main_file(path: str) -> str:
    result=subprocess.run(['git','show','main:'+path],cwd=ROOT,text=True,
                          capture_output=True,check=False)
    if result.returncode:
        raise RuntimeError('Cannot read saved main version: '+result.stderr)
    return result.stdout

def baseline_prompt(task: str, facts: str) -> str:
    # Original v2.1.0 without importing modified example routing or profile.
    original=git_main_file('prompts/writer.md')
    refs='화자 프로필과 긍정형 실행 지침을 바탕으로 고유한 관점을 형성한다.'
    replacements={
        '{{TASK}}':task,
        '{{SOURCES}}':facts,
        '{{STYLE_REFERENCES}}':refs,
        '{{AUTHOR_PROFILE}}':git_main_file('profiles/author-voice.yaml'),
    }
    for key,value in replacements.items():
        original=original.replace(key,value)
    return ('# KOREAN WRITING SKILL\n'+git_main_file('SKILL.md')+'\n\n'
            '# KNOWLEDGE\n'+git_main_file('knowledge/voice-priority.md')+'\n\n'+original)

def no_example_prompt(task: str, facts: str) -> str:
    # Everything else is identical to current, with exemplar/analysis removed.
    refs='화자 프로필과 긍정형 실행 지침을 바탕으로 고유한 관점을 형성한다.'
    text=assemble_writer(task,facts,refs)
    text, n=re.subn(r'# SUCCESSFUL THOUGHT MOVEMENT\n.*?\n\n(?=# 한국어 원고 집필\n)',
                   '',text,flags=re.S)
    if n!=1:
        raise RuntimeError('Could not isolate exemplar analysis block')
    return text

def all_prompts(case: dict) -> dict:
    task=case['task']
    facts=case['facts']
    refs=approved_writer_context(case['genre'],task)
    return {
       'A_v21':baseline_prompt(task,facts),
       'B_current':assemble_writer(task,facts,refs),
       'C_no_example':no_example_prompt(task,facts),
    }

def editor_prompt(draft: str, facts: str) -> str:
    template=(HERE/'cut_only.md').read_text(encoding='utf-8')
    return template.replace('{{DRAFT}}',draft).replace('{{FACTS}}',facts)

def model_call(command: str, prompt: str, timeout: int) -> str:
    parts=shlex.split(command)
    if not parts:
        raise ValueError('model command cannot be empty')
    process=subprocess.run(parts,input=prompt,text=True,capture_output=True,
                           timeout=timeout,check=False)
    if process.returncode:
        raise RuntimeError('Model error: '+process.stderr[-600:])
    if not process.stdout.strip():
        raise RuntimeError('Model returned empty output')
    return process.stdout.strip()

def load_case(case_id: str) -> dict:
    cases=json.loads((HERE/'cases.json').read_text(encoding='utf-8'))
    for case in cases:
        if case['id']==case_id:
            return case
    raise ValueError('Unknown case ID: '+case_id)

def run() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument('--case',required=True)
    parser.add_argument('--output',default='/tmp/writing-ablation')
    parser.add_argument('--model-cmd',default=None,
                        help='External model receiving stdin prompt and returning stdout')
    parser.add_argument('--timeout',type=int,default=180)
    parser.add_argument('--samples',type=int,default=1,
                        help='Independent samples per writing condition (try 3)')
    args=parser.parse_args()
    if args.samples < 1 or args.samples > 5:
        parser.error('--samples must be between 1 and 5')

    case=load_case(args.case)
    dest=Path(args.output).resolve()/case['id']
    dest.mkdir(parents=True,exist_ok=True)
    prompts=all_prompts(case)
    (dest/'case.json').write_text(json.dumps(case,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for name,prompt in prompts.items():
        (dest/(name+'_prompt.md')).write_text(prompt,encoding='utf-8')
    (dest/'D_cut_only_template.md').write_text(
        editor_prompt('{{DRAFT_FROM_B}}',case['facts']),encoding='utf-8')
    (dest/'human_review.md').write_text(
        '# 블라인드 인간 검토\n\n'
        'A/B/C는 조건 이름을 가리고 순서를 섞어 비교한다. D는 B 원고에 대한 삭제 편집이다.\n'
        '질문: (1) 새로운 말이 몇 번 나오는가? (2) 같은 생각의 비유 반복은? '
        '(3) 살아 있는 말투인지? (4) 허구 경험/사실 과장은 없는지?\n'
        '짧다고 자동 가산점, 길다고 자동 감점하지 않는다.\n',encoding='utf-8')
    if args.model_cmd:
        # Do not let a model score its own work, select a winner, or generate
        # a forced 'lesson'. Instead produce comparable independently sampled drafts.
        for sample in range(1,args.samples+1):
            for key,prompt in prompts.items():
                draft=model_call(args.model_cmd,prompt,args.timeout)
                (dest/(key+f'_draft_{sample:02}.md')).write_text(draft+'\n',encoding='utf-8')
                if key=='B_current':
                    edited=model_call(args.model_cmd,editor_prompt(draft,case['facts']),args.timeout)
                    (dest/(f'D_B_cut_draft_{sample:02}.md')).write_text(edited+'\n',encoding='utf-8')
        print('Generated independent drafts; review for actual novelty and naturalness:',dest)
    else:
        print('Prepared prompts only. No model was called:',dest)
    return 0

if __name__=='__main__':
    raise SystemExit(run())
