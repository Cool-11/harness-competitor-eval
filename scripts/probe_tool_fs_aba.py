"""任意 DSH 组件的 A/B/A 机制探针（默认 tool-fs），复用 p0_dsh_isolated 的 patch 机制。

臂序：arm-a1（组件开）→ arm-b（组件关，patch 追加 `- id: <组件>` + `disabled: true`）→ arm-a2（组件开）。
只做运行与归档，不做自动终裁。运行前必须存在预注册文件，且任务目录含 prompt.txt / inputs/ / checker.py。

注意：tool-fs 提供的 read/write/edit/read_image 在 tool-bash 开启时可被 shell 部分替代；
文本型任务下 B 臂可能绕过成功，只有图像型任务能让 tool-fs 成为物理必需。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import secrets
import subprocess
import sys
import time
from pathlib import Path

import cli_batch
import dsh_export
from p0_dsh_isolated import (
    IMAGE, PATCH, REPO, balance, credential, docker, launch_dsh, write,
)

ARMS = ('arm-a1', 'arm-b', 'arm-a2')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frozen_manifest(task_dir: Path, component: str) -> dict:
    inputs = {p.name: sha(p) for p in sorted((task_dir / 'inputs').iterdir()) if p.is_file()}
    record = {
        'variant': task_dir.name,
        'prompt_sha256': sha(task_dir / 'prompt.txt'),
        'checker_sha256': sha(task_dir / 'checker.py'),
        'inputs': inputs, 'image': IMAGE,
    }
    if (task_dir / 'truth.json').is_file():
        record['truth_sha256'] = sha(task_dir / 'truth.json')
    path = task_dir / 'manifest.json'
    if path.is_file() and json.loads(path.read_text(encoding='utf-8')) != record:
        raise ValueError('frozen manifest mismatch; freeze the task package first')
    if not path.is_file():
        write(path, record)
    return record


def off_patch(component: str) -> str:
    return PATCH + f'\n- id: {component}\n  disabled: true\n'


def _pick_session(slot: Path) -> tuple[Path, list[dict]]:
    logs = list((slot / 'sessions').rglob('session*.jsonl*'))
    if not logs:
        raise ValueError('no session logs')
    rows = []
    for path in logs:
        log = dsh_export.resolve_log(path)
        rows.append({'log': str(log), 'events': len(dsh_export.read_events(log))})
    rows.sort(key=lambda row: row['events'], reverse=True)
    write(slot / 'session-candidates.json', rows)
    return Path(rows[0]['log']), dsh_export.read_events(Path(rows[0]['log']))


def _score_arm(task_dir: Path, slot: Path, work: Path) -> tuple[float, float]:
    output = subprocess.run([sys.executable, str(task_dir / 'checker.py'), str(work)],
                            capture_output=True, text=True, encoding='utf-8')
    (slot / 'checker_output.txt').write_text(output.stdout + output.stderr, encoding='utf-8')
    match = re.search(r'产物分合计：([\d.]+)/([\d.]+)', output.stdout)
    return (float(match.group(1)), float(match.group(2))) if match else (0.0, 0.0)


def _run_arm(out: Path, task_dir: Path, component: str, arm: str, index: int, prefix: str,
             network: str, nonce: str, manifest: dict, image_id: str) -> dict:
    slot = out / arm
    slot.mkdir()
    work = slot / 'work'
    work.mkdir()
    for item in sorted((task_dir / 'inputs').iterdir()):
        if item.is_file():
            (work / item.name).write_bytes(item.read_bytes())
    shared = slot / 'shared.yml'
    shared.write_text(off_patch(component) if arm == 'arm-b' else PATCH,
                      encoding='utf-8', newline='\n')
    write(slot / 'configuration.json', {
        'arm': arm, 'only_variable': component,
        'component_state': 'off' if arm == 'arm-b' else 'on',
        'image': IMAGE, 'image_id': image_id, 'shared_patch_sha256': sha(shared),
        'prompt_sha256': manifest['prompt_sha256'], 'inputs_sha256': manifest['inputs'],
        'runtime_work_dir': '/work', 'model': 'deepseek-flash',
        'provider': 'deepseek-official', 'reasoning': 'high',
        'permissions': 'workspace-write',
    })
    name = f'{prefix}-r{index}'
    docker('run', '-d', '--name', name, '--network', network, '--cap-drop', 'ALL',
           '--security-opt', 'no-new-privileges', '--pids-limit', '128', '--memory', '2g',
           '--cpus', '1', '--env', 'DEEPSEEK_API_KEY=' + nonce, IMAGE, 'sleep', 'infinity')
    try:
        docker('cp', str(shared), name + ':/control/shared.yml')
        inspection = json.loads(docker('inspect', name))[0]
        probe = json.loads(docker('exec', name, 'python3', '-c',
            "import pathlib,json;print(json.dumps({'forbidden_present':[str(p) for p in "
            "[pathlib.Path('/tests'),pathlib.Path('/var/run/docker.sock'),"
            "pathlib.Path('F:/for-project-new/harness-competitor-eval')] if p.exists()]}))"))
        if inspection['Mounts'] or inspection['HostConfig']['Privileged'] or probe['forbidden_present']:
            raise ValueError('unsafe container')
        merged = docker('exec', name, 'dsh', '--profile', 'headless', '--patch',
                        '/control/shared.yml', '--dump-config')
        (slot / 'merged-config.yml').write_text(merged, encoding='utf-8')
        for item in sorted(work.iterdir()):
            docker('cp', str(item), name + ':/work/' + item.name)
        start = time.monotonic()
        call = launch_dsh(name, (task_dir / 'prompt.txt').read_text(encoding='utf-8'),
                          slot, 'initial', 600)
        elapsed = time.monotonic() - start
        docker('cp', name + ':/work/.', str(work))
        docker('cp', name + ':/state/home/sessions', str(slot / 'sessions'))
        log, events = _pick_session(slot)
        cwd = next(e['cwd'] for e in events if e.get('type') == 'session')
        observed = cli_batch._dsh_request_context(log)
        got, full = _score_arm(task_dir, slot, work)
        result = {'arm': arm, 'run': index, 'container_id': inspection['Id'], 'cwd': cwd,
                  'observed_context': observed, 'call': call, 'elapsed_seconds': elapsed,
                  'score': {'got': got, 'full': full}, 'archive': str(slot)}
        write(slot / 'run.json', result)
        return result
    finally:
        docker('stop', '--time', '1', name)


def _recover_arm(task_dir: Path, slot: Path, arm: str, index: int) -> dict:
    log, events = _pick_session(slot)
    cwd = next(e['cwd'] for e in events if e.get('type') == 'session')
    observed = cli_batch._dsh_request_context(log)
    got, full = _score_arm(task_dir, slot, slot / 'work')
    result = {'arm': arm, 'run': index, 'recovered': True,
              'note': 'runner crashed after execution; record rebuilt from archived artifacts',
              'cwd': cwd, 'observed_context': observed,
              'score': {'got': got, 'full': full}, 'archive': str(slot)}
    write(slot / 'run.json', result)
    return result


def run(out: Path, task_dir: Path, component: str, prereg: Path,
        resume: bool = False, only: str | None = None, limit_cny: float = 5.0) -> None:
    if not prereg.is_file():
        raise ValueError(f'pre-registration missing: {prereg}')
    if only and only not in ARMS:
        raise ValueError(f'unknown arm: {only}')
    arms_order = [only] if only else list(ARMS)
    if out.exists() and not resume:
        raise ValueError('experiment identity already exists; choose a new --output')
    manifest = frozen_manifest(task_dir, component)
    out.mkdir(parents=True, exist_ok=True)
    key = credential()
    if not (out / 'balance-before.json').is_file():
        write(out / 'balance-before.json', balance(key))
    nonce = secrets.token_hex(24)
    prefix = 'hev-aba-' + secrets.token_hex(5)
    network, proxy = prefix + '-internal', prefix + '-proxy'
    image_id = json.loads(docker('image', 'inspect', IMAGE))[0]['Id']
    write(out / 'plan.json', {'component': component, 'arms': arms_order,
                              'only_variable': component, 'image_id': image_id,
                              'budget_limit_cny': limit_cny,
                              'manifest': manifest, 'preregistration': str(prereg),
                              'task_dir': str(task_dir)})
    docker('network', 'create', '--internal', network)
    docker('run', '-d', '--name', proxy, '--network', 'bridge', '--cap-drop', 'ALL',
           '--security-opt', 'no-new-privileges', IMAGE, 'sleep', 'infinity')
    docker('network', 'connect', '--alias', 'budget-proxy', network, proxy)
    docker('cp', str(REPO / 'scripts/p0_budget_proxy.mjs'), proxy + ':/control/proxy.mjs')
    proxy_log = (out / 'proxy-launch.log').open('w', encoding='utf-8')
    process = subprocess.Popen(['docker', 'exec', '-i', proxy, 'node', '/control/proxy.mjs'],
                               stdin=subprocess.PIPE, stdout=proxy_log, stderr=proxy_log,
                               text=True, encoding='utf-8')
    process.stdin.write(json.dumps({'key': key, 'nonce': nonce, 'limitCny': limit_cny}) + '\n')
    process.stdin.flush()
    process.stdin.close()
    arms: list[dict] = []
    try:
        for _ in range(50):
            if 'READY' in (out / 'proxy-launch.log').read_text(encoding='utf-8'):
                break
            time.sleep(.1)
        else:
            raise ValueError('budget proxy failed to start')
        for arm in arms_order:
            index = ARMS.index(arm) + 1
            slot = out / arm
            if (slot / 'run.json').is_file():
                result = json.loads((slot / 'run.json').read_text(encoding='utf-8'))
            elif slot.is_dir():
                result = _recover_arm(task_dir, slot, arm, index)
            else:
                result = _run_arm(out, task_dir, component, arm, index, prefix, network,
                                  nonce, manifest, image_id)
            arms.append(result)
            full = result['score']['full'] or 7.0
            if arm == 'arm-a1' and result['score']['got'] < full:
                break
            if arm == 'arm-b' and result['score']['got'] > full * 0.15:
                break
        merged: dict[str, dict] = {}
        path = out / 'results.json'
        if path.is_file():
            for row in json.loads(path.read_text(encoding='utf-8')).get('arms', []):
                merged[row['arm']] = row
        for row in arms:
            merged[row['arm']] = row
        if all(arm in merged for arm in ARMS):
            before = set(merged['arm-a1']['observed_context']['tools'])
            after = set(merged['arm-b']['observed_context']['tools'])
            write(out / 'tool-diff.json',
                  {'removed_in_b': sorted(before - after), 'added_in_b': sorted(after - before)})
        write(out / 'results.json', {'status': 'executed_pending_human_review',
                                     'component': component,
                                     'arms': [merged[arm] for arm in ARMS if arm in merged]})
    finally:
        try:
            budget = out / 'budget.jsonl'
            suffix = 1
            while budget.exists():
                suffix += 1
                budget = out / f'budget-run{suffix}.jsonl'
            docker('cp', proxy + ':/state/budget.jsonl', str(budget))
        except subprocess.CalledProcessError:
            pass
        try:
            write(out / 'balance-after.json', balance(key))
        finally:
            docker('stop', '--time', '1', proxy)
            process.wait(timeout=20)
            proxy_log.close()
        write(out / 'container-identities.json',
              {'network': network, 'proxy': proxy, 'retained_for_audit': True})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--task-dir', type=Path, required=True,
                        help='含 prompt.txt / inputs/ / checker.py 的冻结任务目录')
    parser.add_argument('--component', default='tool-fs', help='要开关的 DSH 组件 id')
    parser.add_argument('--preregistration', type=Path, required=True)
    parser.add_argument('--resume', action='store_true', help='补齐已归档臂并继续未执行臂')
    parser.add_argument('--only', choices=ARMS, help='只跑指定臂（每臂独立代理额度）')
    parser.add_argument('--limit-cny', type=float, default=5.0, help='本次代理预算上限（默认 5）')
    args = parser.parse_args()
    run(args.output.resolve(), args.task_dir.resolve(),
        args.component, args.preregistration.resolve(), args.resume,
        args.only, args.limit_cny)
