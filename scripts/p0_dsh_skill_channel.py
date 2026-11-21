"""Bounded, isolated S11 skill-channel single-variable experiment (not automatic adjudication).

Toggles ONLY the DSH skill channel (tool-skill + skill + skill-filesystem) on/off
inside the already read-isolation-verified Linux container. A1/A2 = skill ON,
B = skill OFF. Reuses the isolated-container + budget-proxy infrastructure from
p0_dsh_isolated.py without modifying that frozen script.
"""
from __future__ import annotations

import argparse
import json
import secrets
import subprocess
import time
from pathlib import Path

from p0_dsh_isolated import (IMAGE, REPO, balance, command, credential, docker,
                             launch_dsh, write)

import sbatch
import cli_batch
import dsh_export

# The ONLY difference between arms is the presence/absence of the three skill
# plugin disables. PATCH_SKILL_OFF is byte-identical to run16's shared.yml.
PATCH_SKILL_ON = """- id: llm-deepseek
  config:
    baseURL: http://budget-proxy:9444/anthropic
    maxTokens: 8192
    reasoningEffort: high
- id: session-telemetry-otel
  config:
    mode: DISABLED
"""

PATCH_SKILL_OFF = """- id: llm-deepseek
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

ARMS = [('A1', 'on'), ('B', 'off'), ('A2', 'on')]


def run(out: Path, root: Path):
    if out.exists():
        raise ValueError('experiment identity already exists; choose a new --output')
    if not (REPO / 'experiments/s11-dsh-skill-channel-2026-11-21/preregistration.md').is_file():
        raise ValueError('preregistration missing')
    out.mkdir(parents=True)
    key = credential()
    before = balance(key)
    write(out / 'balance-before.json', before)
    nonce = secrets.token_hex(24)
    prefix = 'hev-s11-skill-' + secrets.token_hex(5)
    network, proxy = prefix + '-internal', prefix + '-proxy'
    docker('network', 'create', '--internal', network)
    docker('run', '-d', '--name', proxy, '--network', 'bridge', '--cap-drop', 'ALL',
           '--security-opt', 'no-new-privileges', IMAGE, 'sleep', 'infinity')
    docker('network', 'connect', '--alias', 'budget-proxy', network, proxy)
    docker('cp', str(REPO / 'scripts/p0_budget_proxy.mjs'), proxy + ':/control/proxy.mjs')
    proxy_log = (out / 'proxy-launch.log').open('w', encoding='utf-8')
    process = subprocess.Popen(['docker', 'exec', '-i', proxy, 'node', '/control/proxy.mjs'],
                               stdin=subprocess.PIPE, stdout=proxy_log, stderr=proxy_log, text=True, encoding='utf-8')
    process.stdin.write(json.dumps({'key': key, 'nonce': nonce}) + '\n')
    process.stdin.flush()
    process.stdin.close()
    on_patch = out / 'skill-on.yml'
    on_patch.write_text(PATCH_SKILL_ON, encoding='utf-8', newline='\n')
    off_patch = out / 'skill-off.yml'
    off_patch.write_text(PATCH_SKILL_OFF, encoding='utf-8', newline='\n')
    image_id = json.loads(docker('image', 'inspect', IMAGE))[0]['Id']
    task = sbatch._resolve('S11')
    frozen_task = sbatch._task_revision(task)
    reserved = [int(p.name[3:]) for parent in (sbatch.SBATCH / task.name / 'dsh', root / task.name / 'dsh')
                for p in parent.glob('run*') if p.name[3:].isdigit()]
    first = max([18, *reserved]) + 1
    plan = {'experiment_id': out.name, 'image_id': image_id, 'task_revision': frozen_task,
            'max_scenes': 3, 'scene_timeout_seconds': 600, 'budget_cny': 5,
            'runs': [first, first + 1, first + 2],
            'only_variable': 'skill_channel',
            'not_comparable_to_windows_p2': True,
            'patch_skill_on_sha256': cli_batch._sha256(on_patch),
            'patch_skill_off_sha256': cli_batch._sha256(off_patch)}
    sources = [REPO / 'scripts/p0_dsh_skill_channel.py', REPO / 'scripts/p0_budget_proxy.mjs',
               REPO / 'scripts/p0-dsh-isolated.Dockerfile',
               REPO / 'experiments/s11-dsh-skill-channel-2026-11-21/preregistration.md',
               on_patch, off_patch]
    plan['frozen_sources'] = {str(p): cli_batch._sha256(p) for p in sources}
    write(out / 'manifest.json', plan)
    results = []
    try:
        for _ in range(50):
            if 'READY' in (out / 'proxy-launch.log').read_text(encoding='utf-8'):
                break
            time.sleep(.1)
        else:
            raise ValueError('budget proxy failed to start')
        for index, (arm, skill) in enumerate(ARMS):
            if sbatch._task_revision(task) != frozen_task:
                raise ValueError('task drift')
            if any(cli_batch._sha256(Path(p)) != digest for p, digest in plan['frozen_sources'].items()):
                raise ValueError('source drift')
            run_number = first + index
            name = prefix + '-' + arm.lower()
            patch_path = on_patch if skill == 'on' else off_patch
            patch_content = PATCH_SKILL_ON if skill == 'on' else PATCH_SKILL_OFF
            docker('run', '-d', '--name', name, '--network', network, '--cap-drop', 'ALL',
                   '--security-opt', 'no-new-privileges', '--pids-limit', '128', '--memory', '2g', '--cpus', '1',
                   '--env', 'DEEPSEEK_API_KEY=' + nonce, IMAGE, 'sleep', 'infinity')
            docker('cp', str(patch_path), name + ':/control/shared.yml')
            inspection = json.loads(docker('inspect', name))[0]
            safe_inspect = {'container_id': inspection['Id'], 'image': inspection['Image'], 'mounts': inspection['Mounts'],
                            'networks': list(inspection['NetworkSettings']['Networks']), 'privileged': inspection['HostConfig']['Privileged']}
            if safe_inspect['mounts'] or safe_inspect['privileged']:
                raise ValueError('unsafe container')
            probe = json.loads(docker('exec', name, 'python3', '-c',
                "import pathlib,json;print(json.dumps({'cwd':str(pathlib.Path.cwd()),'forbidden_present':[str(p) for p in [pathlib.Path('/tests'),pathlib.Path('/app'),pathlib.Path('/var/run/docker.sock'),pathlib.Path('F:/for-project-new/harness-competitor-eval')] if p.exists()],'work_files':[p.name for p in pathlib.Path('/work').iterdir()]}))"))
            if probe['forbidden_present'] or probe['work_files']:
                raise ValueError('contaminated container')
            skills_state = 'enabled' if skill == 'on' else 'disabled'
            config = {'image_id': image_id, 'dsh_version': '0.2.2-rc.1', 'profile': 'headless',
                      'shared_patch': patch_content, 'configuration_id': arm, 'skill_channel': skill,
                      'skills_state': skills_state, 'runtime_work_dir': '/work'}
            config_path = out / f'{arm}-configuration.json'
            write(config_path, config)
            code = sbatch.prepare('S11', 'dsh', run_number, root=root, variant=out.name + '-' + arm,
                model='deepseek-flash', provider='deepseek-official', reasoning='high', sampling='provider_default',
                tools='read,write,bash', permissions='workspace-write', network='internal_network_api_proxy',
                skills_state=skills_state, memory_state='disabled', interface_precheck='passed', surface='cli',
                context_policy='isolated_container', product_version='0.2.2-rc.1',
                configuration_evidence=str(config_path), comparison_track='M_mechanism', admission_track='execution_behavior',
                control_contract=plan, runtime_work_dir='/work')
            if code:
                raise ValueError('prepare rejected')
            work = root / task.name / 'dsh' / f'run{run_number}' / 'work'
            runtime = work.parent / 'runner'
            runtime.mkdir()
            write(runtime / 'container-isolation.json', {'inspect': safe_inspect, 'probe': probe,
                  'network': json.loads(docker('network', 'inspect', network))[0]['Internal']})
            for item in work.iterdir():
                docker('cp', str(item), name + ':/work/' + item.name)
            merged = docker('exec', name, 'dsh', '--profile', 'headless', '--patch', '/control/shared.yml', '--dump-config')
            (runtime / 'merged-config.yml').write_text(merged, encoding='utf-8')
            record = {'arm': arm, 'run': run_number, 'skill_channel': skill, 'container_id': inspection['Id'], 'calls': []}
            start = time.monotonic()
            record['calls'].append(launch_dsh(name, (task / 'prompt.txt').read_text(encoding='utf-8'), runtime, 'initial', 600))
            listing = json.loads(docker('exec', name, 'python3', '-c',
                "import pathlib,json;print(json.dumps([n for n in ['result.md','error_report.md'] if not pathlib.Path(n).is_file() or pathlib.Path(n).stat().st_size==0]))"))
            record['missing_initial'] = listing
            if any(cli_batch._sha256(Path(p)) != digest for p, digest in plan['frozen_sources'].items()):
                raise ValueError('source drift after execution')
            docker('cp', name + ':/work/.', str(work))
            docker('cp', name + ':/state/home/sessions', str(runtime / 'sessions'))
            logs = list((runtime / 'sessions').rglob('session*.jsonl*'))
            if len({p.parent for p in logs}) != 1:
                raise ValueError('session identity not unique')
            log = dsh_export.resolve_log(logs[0])
            events = dsh_export.read_events(log)
            cwd = next(e['cwd'] for e in events if e.get('type') == 'session')
            observed = cli_batch._dsh_request_context(log)
            record.update(observed_context=observed, observed_cwd=cwd, elapsed_seconds=time.monotonic() - start,
                          skill_tool_observed='skill' in observed['tools'])
            write(runtime / 'native-evidence.json', record)
            code = sbatch.collect('S11', 'dsh', run_number, str(work), observed_cwd=cwd,
                cwd_evidence=str(runtime / 'native-evidence.json'), evidence_mode='native_trace',
                session_export=str(log), configuration_evidence=str(config_path),
                observed_model=observed['model'], observed_provider=observed['provider'], observed_reasoning=observed['reasoning'],
                observed_sampling=observed['sampling'], observed_tools=observed['tools'], observed_permissions=observed['permissions'],
                observed_context_source=observed['source'], turns=len(record['calls']), elapsed=record['elapsed_seconds'],
                timed_out=any(c['timed_out'] for c in record['calls']),
                termination='product_declared_done' if record['calls'][-1]['returncode'] == 0 else 'error')
            if code:
                raise ValueError('collect rejected; preserve container and raw work')
            archived = sbatch.SBATCH / task.name / 'dsh' / f'run{run_number}'
            score = json.loads((archived / 'score.json').read_text(encoding='utf-8'))
            record['score'] = score
            record['archive'] = str(archived)
            record['adjudication'] = 'pending'
            results.append(record)
            write(out / 'results.json', {'status': 'executed_pending_human_review', 'runs': results})
            docker('stop', '--time', '1', name)
            if any(c['returncode'] != 0 or c['timed_out'] for c in record['calls']):
                break
            if observed['model'] != 'deepseek-flash' or observed['reasoning'] != 'high':
                break
            raw = score.get('raw_got')
            full = score.get('raw_full')
            if arm == 'A1' and raw == full:
                break  # skill ON did not reproduce the miss -> skill not necessary
            if arm == 'B' and raw != full:
                break  # skill OFF still failed -> anomaly, skill not sufficient
    finally:
        try:
            docker('cp', proxy + ':/state/budget.jsonl', str(out / 'budget.jsonl'))
        except subprocess.CalledProcessError:
            pass
        try:
            write(out / 'balance-after.json', balance(key))
        finally:
            docker('stop', '--time', '1', proxy)
            process.wait(timeout=20)
            proxy_log.close()
        write(out / 'container-identities.json', {'network': network, 'proxy': proxy, 'retained_for_audit': True})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    run(args.output.resolve(), args.root.resolve())
