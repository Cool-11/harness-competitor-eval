"""Run the separately preregistered S11 C1 follow-up; never auto-adjudicate."""
from __future__ import annotations

import argparse
import json
import secrets
import subprocess
import time
from pathlib import Path

import cli_batch
import dsh_export
import p0_dsh_isolated as base
import sbatch


REPO = Path(__file__).resolve().parents[1]
EXPERIMENT = REPO / 'experiments/p0-dsh-isolated-2026-11-20'
ORIGINAL = EXPERIMENT / 'execution-01'
ADDENDUM = EXPERIMENT / 'preregistration-addendum-01.md'
PROXY = REPO / 'scripts/p0_budget_proxy_followup.mjs'


def _prior() -> tuple[dict, float]:
    manifest = json.loads((ORIGINAL / 'manifest.json').read_text(encoding='utf-8'))
    for filename, digest in manifest['frozen_sources'].items():
        if cli_batch._sha256(Path(filename)) != digest:
            raise ValueError(f'original frozen source drift: {filename}')
    runs = json.loads((ORIGINAL / 'results.json').read_text(encoding='utf-8'))['runs']
    if len(runs) != 1 or runs[0]['arm'] != 'C0' or runs[0]['run'] != 16:
        raise ValueError('original baseline identity changed')
    if runs[0]['score']['raw_got'] != 7 or runs[0]['score']['raw_full'] != 7:
        raise ValueError('original baseline is not mechanical full score')
    record = sbatch.SBATCH / 'S11-corrupt-recovery/dsh/run16/manifest.json'
    archived = json.loads(record.read_text(encoding='utf-8'))
    if archived['run_id'] != 'hev-20261120T214236+0800-S11-dsh-r16-36035514':
        raise ValueError('original run ID changed')
    entries = [json.loads(line) for line in (ORIGINAL / 'budget.jsonl').read_text(encoding='utf-8').splitlines()]
    reservations = [row['cumulative_reserved_cny'] for row in entries if row.get('event') == 'reservation']
    if len(reservations) != 9 or abs(reservations[-1] - 1.57044) > 1e-8:
        raise ValueError('original budget carryover changed')
    return manifest, reservations[-1]


def run(out: Path, root: Path) -> None:
    if out.exists():
        raise ValueError('follow-up output already exists')
    original, carryover = _prior()
    task = sbatch._resolve('S11')
    if sbatch._task_revision(task) != original['task_revision']:
        raise ValueError('task revision drift')
    image_id = json.loads(base.docker('image', 'inspect', base.IMAGE))[0]['Id']
    if image_id != original['image_id']:
        raise ValueError('image drift')
    if (ORIGINAL / 'shared.yml').read_text(encoding='utf-8') != base.PATCH:
        raise ValueError('shared patch drift')
    run_number = 17
    if (sbatch.SBATCH / task.name / 'dsh' / f'run{run_number}').exists() or (root / task.name / 'dsh' / f'run{run_number}').exists():
        raise ValueError('run17 occupied; do not overwrite or silently reassign')
    key = base.credential()
    before = base.balance(key)
    out.mkdir(parents=True)
    base.write(out / 'balance-before.json', before)
    shared = out / 'shared.yml'
    shared.write_text(base.PATCH, encoding='utf-8', newline='\n')
    source_paths = [Path(__file__), PROXY, ADDENDUM, ORIGINAL / 'manifest.json', shared,
                    REPO / 'scripts/p0_dsh_isolated.py', REPO / 'scripts/p0-dsh-isolated.Dockerfile']
    frozen = {str(path): cli_batch._sha256(path) for path in source_paths}
    plan = {'experiment_id': out.name, 'original_experiment': str(ORIGINAL),
            'original_run_id': 'hev-20261120T214236+0800-S11-dsh-r16-36035514',
            'arm': 'C1', 'run': run_number, 'task_revision': original['task_revision'],
            'image_id': image_id, 'shared_patch_sha256': cli_batch._sha256(shared),
            'only_variable': 'external_delivery_gate', 'max_new_scenes': 1,
            'scene_timeout_seconds': 600, 'budget_cny_cumulative': 5,
            'carryover_reserved_cny': carryover, 'frozen_sources': frozen,
            'inference_scope': 'non_regression_or_gate_activation_only_no_repair_effect'}
    base.write(out / 'manifest.json', plan)
    nonce = secrets.token_hex(24)
    prefix = 'hev-p0a-' + secrets.token_hex(5)
    network, proxy, name = prefix + '-internal', prefix + '-proxy', prefix + '-c1'
    base.docker('network', 'create', '--internal', network)
    base.docker('run', '-d', '--name', proxy, '--network', 'bridge', '--cap-drop', 'ALL',
                '--security-opt', 'no-new-privileges', base.IMAGE, 'sleep', 'infinity')
    base.docker('network', 'connect', '--alias', 'budget-proxy', network, proxy)
    base.docker('cp', str(PROXY), proxy + ':/control/proxy.mjs')
    proxy_log = (out / 'proxy-launch.log').open('w', encoding='utf-8')
    process = subprocess.Popen(['docker', 'exec', '-i', proxy, 'node', '/control/proxy.mjs'],
                               stdin=subprocess.PIPE, stdout=proxy_log, stderr=proxy_log,
                               text=True, encoding='utf-8')
    process.stdin.write(json.dumps({'key': key, 'nonce': nonce, 'carryoverReservedCny': carryover}) + '\n')
    process.stdin.flush()
    process.stdin.close()
    try:
        for _ in range(50):
            if 'READY' in (out / 'proxy-launch.log').read_text(encoding='utf-8'):
                break
            time.sleep(.1)
        else:
            raise ValueError('budget proxy failed to start')
        if sbatch._task_revision(task) != plan['task_revision'] or any(
            cli_batch._sha256(Path(path)) != digest for path, digest in frozen.items()
        ):
            raise ValueError('source or task drift before prepare')
        base.docker('run', '-d', '--name', name, '--network', network, '--cap-drop', 'ALL',
                    '--security-opt', 'no-new-privileges', '--pids-limit', '128',
                    '--memory', '2g', '--cpus', '1', '--env', 'DEEPSEEK_API_KEY=' + nonce,
                    base.IMAGE, 'sleep', 'infinity')
        base.docker('cp', str(shared), name + ':/control/shared.yml')
        inspection = json.loads(base.docker('inspect', name))[0]
        safe = {'container_id': inspection['Id'], 'image': inspection['Image'],
                'mounts': inspection['Mounts'], 'networks': list(inspection['NetworkSettings']['Networks']),
                'privileged': inspection['HostConfig']['Privileged']}
        if safe['mounts'] or safe['privileged'] or safe['networks'] != [network]:
            raise ValueError('unsafe product container')
        probe = json.loads(base.docker('exec', name, 'python3', '-c',
            "import pathlib,json;print(json.dumps({'cwd':str(pathlib.Path.cwd()),'forbidden_present':[str(p) for p in [pathlib.Path('/tests'),pathlib.Path('/app'),pathlib.Path('/var/run/docker.sock'),pathlib.Path('F:/for-project-new/harness-competitor-eval')] if p.exists()],'work_files':[p.name for p in pathlib.Path('/work').iterdir()]}))"))
        if probe['forbidden_present'] or probe['work_files']:
            raise ValueError('contaminated container')
        config_path = out / 'C1-configuration.json'
        base.write(config_path, {'image_id': image_id, 'dsh_version': '0.2.2-rc.1',
                                'profile': 'headless', 'shared_patch': base.PATCH,
                                'configuration_id': 'C1', 'delivery_gate': True,
                                'runtime_work_dir': '/work'})
        code = sbatch.prepare('S11', 'dsh', run_number, root=root, variant=out.name + '-C1',
            model='deepseek-flash', provider='deepseek-official', reasoning='high',
            sampling='provider_default', tools='read,write,bash', permissions='workspace-write',
            network='internal_network_api_proxy', skills_state='disabled', memory_state='disabled',
            interface_precheck='passed', surface='cli', context_policy='isolated_container',
            product_version='0.2.2-rc.1', configuration_evidence=str(config_path),
            comparison_track='M_mechanism', admission_track='execution_behavior',
            control_contract=plan, runtime_work_dir='/work')
        if code:
            raise ValueError('prepare rejected')
        work = root / task.name / 'dsh' / f'run{run_number}' / 'work'
        runtime = work.parent / 'runner'
        runtime.mkdir()
        base.write(runtime / 'container-isolation.json', {'inspect': safe, 'probe': probe,
            'network': json.loads(base.docker('network', 'inspect', network))[0]['Internal']})
        for item in work.iterdir():
            base.docker('cp', str(item), name + ':/work/' + item.name)
        merged = base.docker('exec', name, 'dsh', '--profile', 'headless', '--patch',
                             '/control/shared.yml', '--dump-config')
        (runtime / 'merged-config.yml').write_text(merged, encoding='utf-8')
        record = {'arm': 'C1', 'run': run_number, 'container_id': inspection['Id'], 'calls': []}
        start = time.monotonic()
        record['calls'].append(base.launch_dsh(name, (task / 'prompt.txt').read_text(encoding='utf-8'),
                                               runtime, 'initial', 600))
        missing = json.loads(base.docker('exec', name, 'python3', '-c',
            "import pathlib,json;print(json.dumps([n for n in ['result.md','error_report.md'] if not pathlib.Path(n).is_file() or pathlib.Path(n).stat().st_size==0]))"))
        record['missing_initial'] = missing
        if sbatch._task_revision(task) != plan['task_revision'] or any(
            cli_batch._sha256(Path(path)) != digest for path, digest in frozen.items()
        ):
            raise ValueError('source or task drift after initial run')
        if missing and record['calls'][0]['returncode'] == 0 and not record['calls'][0]['timed_out']:
            base.docker('cp', name + ':/state/home/sessions', str(runtime / 'sessions-before-repair'))
            logs = list((runtime / 'sessions-before-repair').rglob('session*.jsonl*'))
            events = dsh_export.read_events(dsh_export.resolve_log(logs[0]))
            session = next(event['id'] for event in events if event.get('type') == 'session')
            remaining = 600 - (time.monotonic() - start)
            if remaining > 0:
                feedback = '交付前检查发现工作目录根目录缺少或留空以下题面要求的文件：' + '、'.join(missing) + '。请依据原任务补齐这些文件并核对位置和内容；不要把聊天回复当作文件。'
                (runtime / 'feedback.txt').write_text(feedback, encoding='utf-8')
                record['calls'].append(base.launch_dsh(name, feedback, runtime, 'repair', remaining, session))
        base.docker('cp', name + ':/work/.', str(work))
        base.docker('cp', name + ':/state/home/sessions', str(runtime / 'sessions'))
        logs = list((runtime / 'sessions').rglob('session*.jsonl*'))
        if len({path.parent for path in logs}) != 1:
            raise ValueError('session identity not unique')
        log = dsh_export.resolve_log(logs[0])
        events = dsh_export.read_events(log)
        cwd = next(event['cwd'] for event in events if event.get('type') == 'session')
        observed = cli_batch._dsh_request_context(log)
        record.update(observed_context=observed, observed_cwd=cwd,
                      elapsed_seconds=time.monotonic() - start)
        base.write(runtime / 'native-evidence.json', record)
        code = sbatch.collect('S11', 'dsh', run_number, str(work), observed_cwd=cwd,
            cwd_evidence=str(runtime / 'native-evidence.json'), evidence_mode='native_trace',
            session_export=str(log), configuration_evidence=str(config_path),
            observed_model=observed['model'], observed_provider=observed['provider'],
            observed_reasoning=observed['reasoning'], observed_sampling=observed['sampling'],
            observed_tools=observed['tools'], observed_permissions=observed['permissions'],
            observed_context_source=observed['source'], turns=len(record['calls']),
            elapsed=record['elapsed_seconds'],
            timed_out=any(call['timed_out'] for call in record['calls']),
            termination='product_declared_done' if record['calls'][-1]['returncode'] == 0 else 'error')
        if code:
            raise ValueError('collect rejected; preserve raw container and files')
        archived = sbatch.SBATCH / task.name / 'dsh' / f'run{run_number}'
        record['score'] = json.loads((archived / 'score.json').read_text(encoding='utf-8'))
        record['archive'] = str(archived)
        record['adjudication'] = 'pending'
        base.write(out / 'results.json', {'status': 'executed_pending_human_review', 'runs': [record]})
        base.docker('stop', '--time', '1', name)
    finally:
        try:
            base.docker('cp', proxy + ':/state/budget.jsonl', str(out / 'budget.jsonl'))
        except subprocess.CalledProcessError:
            pass
        try:
            base.write(out / 'balance-after.json', base.balance(key))
        finally:
            base.docker('stop', '--time', '1', proxy)
            process.wait(timeout=20)
            proxy_log.close()
        base.write(out / 'container-identities.json', {'network': network, 'proxy': proxy,
            'product': name, 'retained_for_audit': True})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    run(args.output.resolve(), args.root.resolve())
