"""Bounded, isolated S06 external delivery-check experiment (not adjudication)."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import subprocess
import sys
import time
from pathlib import Path

import sbatch
import cli_batch
import dsh_export

REPO = Path(__file__).resolve().parents[1]
IMAGE = 'harness-p0-dsh:20261120'
PATCH = """- id: llm-deepseek
  config:
    baseURL: http://budget-proxy:9444/anthropic
    maxTokens: 8192
    reasoningEffort: high
- id: skill
  disabled: true
- id: skill-filesystem
  disabled: true
- id: tool-skill
  disabled: true
- id: session-telemetry-otel
  config:
    mode: DISABLED
"""


def command(args, **kwargs):
    return subprocess.run(args, check=True, capture_output=True, encoding='utf-8', **kwargs).stdout


def docker(*args, **kwargs):
    return command(['docker', *args], **kwargs)


def write(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def credential() -> str:
    # Subprocess output is captured in memory and never emitted into audit logs.
    package = Path(os.environ['APPDATA']) / 'npm/node_modules/@deepseek-ai/dsh/package.json'
    script = "const r=require('module').createRequire(process.argv[1]);const d=r('yaml').parse(require('fs').readFileSync(process.argv[2],'utf8'));process.stdout.write(d.refs.DEEPSEEK_API_KEY);"
    return command(['node', '-e', script, str(package), str(Path.home()/'.dsh/.credentials.yaml')]).strip()


def balance(key: str) -> dict:
    script = "let s='';for await(const c of process.stdin)s+=c;const r=await fetch('https://api.deepseek.com/user/balance',{headers:{Authorization:'Bearer '+s},signal:AbortSignal.timeout(20000)});if(!r.ok)process.exit(2);console.log(JSON.stringify(await r.json()));"
    return json.loads(command(['node', '--input-type=module', '-e', script], input=key))


def launch_dsh(name: str, prompt: str, runtime: Path, label: str, timeout: float, session: str = '') -> dict:
    args=['docker','exec','-i','-w','/work',name,'dsh','--profile','headless','--patch','/control/shared.yml',
          '--permission-mode','workspace-write','--approval-policy','never']
    if session:
        args += ['--session-id',session]
    args.append(prompt)
    started=time.monotonic()
    with (runtime/f'{label}.stdout.txt').open('w',encoding='utf-8') as stdout, (runtime/f'{label}.stderr.txt').open('w',encoding='utf-8') as stderr:
        process=subprocess.Popen(args,stdout=stdout,stderr=stderr,encoding='utf-8')
        timed_out=False
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out=True
            docker('stop','--time','1',name)
            process.wait(timeout=20)
    return {'returncode':process.returncode,'timed_out':timed_out,'elapsed_seconds':time.monotonic()-started}


def run(out: Path, root: Path):
    if out.exists():
        raise ValueError('experiment identity already exists; choose a new --output')
    prereg=REPO/'experiments/dsh-v41flash-2026-11-21/s06-gate-preregistration.md'
    if not prereg.is_file():
        raise ValueError('preregistration missing')
    deadline=time.monotonic()+120
    out.mkdir(parents=True)
    key=credential()
    before=balance(key)
    write(out/'balance-before.json',before)
    nonce=secrets.token_hex(24)
    prefix='hev-p0-'+secrets.token_hex(5)
    network,proxy=prefix+'-internal',prefix+'-proxy'
    docker('network','create','--internal',network)
    docker('run','-d','--name',proxy,'--network','bridge','--cap-drop','ALL','--security-opt','no-new-privileges',IMAGE,'sleep','infinity')
    docker('network','connect','--alias','budget-proxy',network,proxy)
    docker('cp',str(REPO/'scripts/s06_gate_budget_proxy.mjs'),proxy+':/control/proxy.mjs')
    proxy_log=(out/'proxy-launch.log').open('w',encoding='utf-8')
    process=subprocess.Popen(['docker','exec','-i',proxy,'node','/control/proxy.mjs'],stdin=subprocess.PIPE,stdout=proxy_log,stderr=proxy_log,text=True,encoding='utf-8')
    process.stdin.write(json.dumps({'key':key,'nonce':nonce})+'\n');process.stdin.flush();process.stdin.close()
    shared=out/'shared.yml';shared.write_text(PATCH,encoding='utf-8',newline='\n')
    image_id=json.loads(docker('image','inspect',IMAGE))[0]['Id']
    task=sbatch._resolve('S06')
    frozen_task=sbatch._task_revision(task)
    reserved=[int(p.name[3:]) for parent in (sbatch.SBATCH/task.name/'dsh',root/task.name/'dsh') for p in parent.glob('run*') if p.name[3:].isdigit()]
    first=max([4,*reserved])+1
    plan={'experiment_id':out.name,'image_id':image_id,'task_revision':frozen_task,
          'max_scenes':3,'total_timeout_seconds':120,'budget_cny':2,'runs':[first,first+1,first+2],
          'only_variable':'external_s06_delivery_check','shared_patch_sha256':cli_batch._sha256(shared),
          'not_comparable_to_windows_p2':True}
    sources=[REPO/'scripts/s06_gate_v41.py',REPO/'scripts/s06_gate_budget_proxy.mjs',REPO/'scripts/p0-dsh-isolated.Dockerfile',prereg,shared]
    plan['frozen_sources']={str(p):cli_batch._sha256(p) for p in sources}
    write(out/'manifest.json',plan)
    results=[]
    try:
        # Proxy readiness is a filesystem observation; it never calls a model.
        for _ in range(50):
            if 'READY' in (out/'proxy-launch.log').read_text(encoding='utf-8'):break
            time.sleep(.1)
        else:raise ValueError('budget proxy failed to start')
        for index,arm in enumerate(('C0','C1','C0-restored')):
            if deadline-time.monotonic() < 15: break
            if sbatch._task_revision(task)!=frozen_task:raise ValueError('task drift')
            if any(cli_batch._sha256(Path(p))!=digest for p,digest in plan['frozen_sources'].items()):raise ValueError('source drift')
            run_number=first+index; name=prefix+'-'+arm.lower()
            docker('run','-d','--name',name,'--network',network,'--cap-drop','ALL','--security-opt','no-new-privileges',
                   '--pids-limit','128','--memory','2g','--cpus','1','--env','DEEPSEEK_API_KEY='+nonce,IMAGE,'sleep','infinity')
            docker('cp',str(shared),name+':/control/shared.yml')
            inspection=json.loads(docker('inspect',name))[0]
            safe_inspect={'container_id':inspection['Id'],'image':inspection['Image'],'mounts':inspection['Mounts'],
                          'networks':list(inspection['NetworkSettings']['Networks']),'privileged':inspection['HostConfig']['Privileged']}
            if safe_inspect['mounts'] or safe_inspect['privileged']:raise ValueError('unsafe container')
            if docker('exec',name,'dsh','--version').strip()!='0.2.2-rc.1':raise ValueError('DSH version drift')
            probe=json.loads(docker('exec',name,'python3','-c',
                "import pathlib,json;print(json.dumps({'cwd':str(pathlib.Path.cwd()),'forbidden_present':[str(p) for p in [pathlib.Path('/tests'),pathlib.Path('/app'),pathlib.Path('/var/run/docker.sock'),pathlib.Path('F:/for-project-new/harness-competitor-eval')] if p.exists()],'work_files':[p.name for p in pathlib.Path('/work').iterdir()]}))"))
            if probe['forbidden_present'] or probe['work_files']:raise ValueError('contaminated container')
            config={'image_id':image_id,'dsh_version':'0.2.2-rc.1','profile':'headless','shared_patch':PATCH,
                    'configuration_id':'C1' if arm=='C1' else 'C0','delivery_gate':arm=='C1','runtime_work_dir':'/work'}
            config_path=out/f'{arm}-configuration.json';write(config_path,config)
            code=sbatch.prepare('S06','dsh',run_number,root=root,variant=out.name+'-'+arm,model='deepseek-flash',
                provider='deepseek-official',reasoning='high',sampling='provider_default',tools='read,write,bash',
                permissions='workspace-write',network='internal_network_api_proxy',skills_state='disabled',memory_state='disabled',
                interface_precheck='passed',surface='cli',context_policy='isolated_container',product_version='0.2.2-rc.1',
                configuration_evidence=str(config_path),comparison_track='B_native_product',admission_track='execution_behavior',
                control_contract=plan,runtime_work_dir='/work')
            if code:raise ValueError('prepare rejected')
            work=root/task.name/'dsh'/f'run{run_number}'/'work';runtime=work.parent/'runner';runtime.mkdir()
            write(runtime/'container-isolation.json',{'inspect':safe_inspect,'probe':probe,'network':json.loads(docker('network','inspect',network))[0]['Internal']})
            for item in work.iterdir():docker('cp',str(item),name+':/work/'+item.name)
            merged=docker('exec',name,'dsh','--profile','headless','--patch','/control/shared.yml','--dump-config')
            (runtime/'merged-config.yml').write_text(merged,encoding='utf-8')
            record={'arm':arm,'run':run_number,'container_id':inspection['Id'],'calls':[]}
            start=time.monotonic()
            remaining=deadline-time.monotonic()
            if remaining < 5:
                write(out/'stop-before-call.json',{'arm':arm,'remaining_seconds':remaining})
                docker('stop','--time','1',name)
                break
            record['calls'].append(launch_dsh(name,(task/'prompt.txt').read_text(encoding='utf-8'),runtime,'initial',remaining))
            if record['calls'][0]['timed_out']:
                write(runtime/'timeout-before-collect.json',record)
                raise ValueError('total time limit reached; preserve product container and prepared run')
            check_script="import pathlib,json;p=pathlib.Path('输出/汇总/月报_v1.md');lines=p.read_text(encoding='utf-8').splitlines() if p.is_file() else [];first=next((s for s in lines if s.strip()),'');print(json.dumps({'missing':not p.is_file(),'empty':not bool(lines),'wrong_title':bool(first) and first!='# 九月月报'}))"
            gate=json.loads(docker('exec','-w','/work',name,'python3','-c',check_script))
            record['gate_initial']=gate
            if any(cli_batch._sha256(Path(p))!=digest for p,digest in plan['frozen_sources'].items()):raise ValueError('source drift after execution')
            if arm=='C1' and any(gate.values()) and record['calls'][0]['returncode']==0 and not record['calls'][0]['timed_out']:
                docker('cp',name+':/state/home/sessions',str(runtime/'sessions-before-repair'))
                logs=list((runtime/'sessions-before-repair').rglob('session*.jsonl*'))
                events=dsh_export.read_events(dsh_export.resolve_log(logs[0]))
                session=next(e['id'] for e in events if e.get('type')=='session')
                remaining=deadline-time.monotonic()
                if remaining>5:
                    feedback='交付前检查发现题面指定的 输出/汇总/月报_v1.md 缺失、为空或首个非空行不是 # 九月月报。请依据原任务补齐并核对标题、位置与内容；不要把聊天回复当作文件。'
                    (runtime/'feedback.txt').write_text(feedback,encoding='utf-8')
                    record['calls'].append(launch_dsh(name,feedback,runtime,'repair',remaining,session))
            docker('cp',name+':/work/.',str(work))
            docker('cp',name+':/state/home/sessions',str(runtime/'sessions'))
            logs=list((runtime/'sessions').rglob('session*.jsonl*'))
            if len({p.parent for p in logs})!=1:raise ValueError('session identity not unique')
            log=dsh_export.resolve_log(logs[0]);events=dsh_export.read_events(log)
            cwd=next(e['cwd'] for e in events if e.get('type')=='session')
            observed=cli_batch._dsh_request_context(log)
            record.update(observed_context=observed,observed_cwd=cwd,elapsed_seconds=time.monotonic()-start)
            write(runtime/'native-evidence.json',record)
            code=sbatch.collect('S06','dsh',run_number,str(work),observed_cwd=cwd,cwd_evidence=str(runtime/'native-evidence.json'),
                evidence_mode='native_trace',session_export=str(log),configuration_evidence=str(config_path),
                observed_model=observed['model'],observed_provider=observed['provider'],observed_reasoning=observed['reasoning'],
                observed_sampling=observed['sampling'],observed_tools=observed['tools'],observed_permissions=observed['permissions'],
                observed_context_source=observed['source'],turns=len(record['calls']),elapsed=record['elapsed_seconds'],
                timed_out=any(c['timed_out'] for c in record['calls']),termination='product_declared_done' if record['calls'][-1]['returncode']==0 else 'error')
            if code:raise ValueError('collect rejected; preserve container and raw work')
            archived=sbatch.SBATCH/task.name/'dsh'/f'run{run_number}'
            score=json.loads((archived/'score.json').read_text(encoding='utf-8'))
            record['score']=score;record['archive']=str(archived);record['adjudication']='pending'
            budget_events=[json.loads(line) for line in docker('exec',proxy,'cat','/state/budget.jsonl').splitlines()]
            record['budget_blocked']=any(event.get('event')=='blocked_or_error' for event in budget_events)
            results.append(record);write(out/'results.json',{'status':'executed_pending_human_review','runs':results})
            docker('stop','--time','1',name)
            if record['budget_blocked']:break
            if any(c['returncode']!=0 or c['timed_out'] for c in record['calls']):break
            if observed['model']!='deepseek-flash' or observed['reasoning']!='high':break
            raw=score.get('raw_got');full=score.get('raw_full')
            if arm=='C0' and (raw==full or not any(gate.values())):break
            if arm=='C1' and (raw!=full or len(record['calls'])<2):break
    finally:
        try:docker('cp',proxy+':/state/budget.jsonl',str(out/'budget.jsonl'))
        except subprocess.CalledProcessError:pass
        try:write(out/'balance-after.json',balance(key))
        finally:
            docker('stop','--time','1',proxy)
            process.wait(timeout=20);proxy_log.close()
        write(out/'container-identities.json',{'network':network,'proxy':proxy,'retained_for_audit':True})


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--root',type=Path,required=True)
    args=parser.parse_args()
    run(args.output.resolve(),args.root.resolve())
