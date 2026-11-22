#!/usr/bin/env python3
"""Voice-locked observation experiment. Does not edit baseline writing skill.

Steps: generate angle card; run unchanged v2.1 writer prompt with/without
one selected observation; human compare drafts. Offline prepare/build supported.
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
sys.path.insert(0,str(ROOT/'scripts'))
from run_pipeline import assemble_writer, approved_writer_context, load_text

REQUIRED=('observation','concrete_moment','speaker_stance',
          'emotional_turn','fact_boundary','why_this_is_worth_telling')


def angle_prompt(task: str,sources: str) -> str:
    src=load_text(Path(__file__).with_name('angle_prompt.md'))
    return src.replace('{{TASK}}',task).replace('{{SOURCES}}',sources)


def parse_card(text: str) -> dict:
    raw=text.strip()
    raw=re.sub(r'^\x60\x60\x60(?:json)?\s*','',raw)
    raw=re.sub(r'\s*\x60\x60\x60$','',raw)
    data=json.loads(raw)
    if not isinstance(data,dict) or any(not isinstance(data.get(k),str) or not data[k].strip() for k in REQUIRED):
        raise ValueError('Angle card requires six nonempty text fields')
    if any(len(data[k])>600 for k in REQUIRED):
        raise ValueError('Angle card should contain short, focused observations')
    return {key:data[key].strip() for key in REQUIRED}


def variant_task(task: str,card: dict) -> str:
    # Only a brief topic-specific thought is passed to the ORIGINAL writer.
    # The writer's style guide, knowledge file, template and role stay identical.
    return (task+'\n\n취재하면서 떠오른 생각 (이것을 꼭 순서대로 옮겨 쓸 필요는 없음):\n'
            +'처음 눈에 들어온 장면: '+card['concrete_moment']+'\n'
            +'이 장면에서 발견한 점: '+card['observation']+'\n'
            +'왜 이 이야기가 하고 싶은가: '+card['speaker_stance']+'; '+card['why_this_is_worth_telling']+'\n'
            +'감정이나 판단이 바뀌는 순간: '+card['emotional_turn']+'\n'
            +'근거의 경계: '+card['fact_boundary'])


def pair_prompts(task: str, genre: str, sources: str, card: dict | None=None) -> dict:
    ref=approved_writer_context(genre,task)
    output={'baseline':assemble_writer(task,sources,ref)}
    if card is not None:
        output['variant']=assemble_writer(variant_task(task,card),sources,ref)
    return output


def model_call(command: str,prompt: str,timeout: int) -> str:
    args=shlex.split(command)
    if not args: raise ValueError('model command is empty')
    result=subprocess.run(args,input=prompt,capture_output=True,text=True,encoding='utf-8',
                          timeout=timeout,check=False)
    if result.returncode or not result.stdout.strip():
        raise RuntimeError('model returned error: '+result.stderr[-500:])
    return result.stdout.strip()


def main() -> int:
    ap=argparse.ArgumentParser(description='Voice-locked angle stage test')
    ap.add_argument('--task',required=True)
    ap.add_argument('--genre',default='건강정보')
    ap.add_argument('--sources-file',required=True)
    ap.add_argument('--mode',choices=('prepare','build','run'),default='prepare')
    ap.add_argument('--angle-file',help='JSON observation card from idea stage')
    ap.add_argument('--model-cmd',help='CLI accepting text prompt on stdin; required for run')
    ap.add_argument('--timeout',type=int,default=180)
    ap.add_argument('--output',default='writing_experiment')
    args=ap.parse_args()
    source=Path(args.sources_file).read_text(encoding='utf-8')
    out=Path(args.output).resolve()
    out.mkdir(parents=True,exist_ok=True)
    idea=angle_prompt(args.task,source)
    (out/'01_angle_prompt.md').write_text(idea,encoding='utf-8')
    base=pair_prompts(args.task,args.genre,source)
    (out/'02_baseline_writer_prompt.md').write_text(base['baseline'],encoding='utf-8')
    if args.mode=='prepare':
        print('Prepared angle prompt and baseline. Supply an angle JSON with --mode build --angle-file.')
        return 0
    if args.mode=='run':
        if not args.model_cmd: ap.error('--mode run requires --model-cmd')
        raw=model_call(args.model_cmd,idea,args.timeout)
        (out/'angle_raw.txt').write_text(raw+'\n',encoding='utf-8')
        card=parse_card(raw)
        (out/'angle_card.json').write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:
        if not args.angle_file: ap.error('--mode build requires --angle-file')
        card=parse_card(Path(args.angle_file).read_text(encoding='utf-8'))
    prompts=pair_prompts(args.task,args.genre,source,card)
    (out/'03_variant_writer_prompt.md').write_text(prompts['variant'],encoding='utf-8')
    if args.mode=='run':
        # Baseline and variant use the same exact model CLI and full facts.
        for key,filename in [('baseline','04_baseline_draft.md'),('variant','05_variant_draft.md')]:
            result=model_call(args.model_cmd,prompts[key],args.timeout)
            (out/filename).write_text(result+'\n',encoding='utf-8')
        print('Drafts created. Compare blind: topic-specific observation, emotions, voice, factual scope.')
    else:
        print('Prepared variant writer prompt. Paste it into the same model as baseline.')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
