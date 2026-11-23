"""tool-bash A/B/A 机制探针：三臂顺序执行并归档。

arm-a1（tool-bash 开）→ arm-b（tool-bash 关）→ arm-a2（tool-bash 开）。
只做运行与归档，不做自动终裁。
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

EXPERIMENT = REPO / 'experiments/mechanism-probe-tool-bash-2026-11-23'
ARMS = ('arm-a1', 'arm-b', 'arm-a2')
OFF_PATCH = PATCH + '\n- id: tool-bash\n  disabled: true\n'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frozen_manifest() -> dict:
    record = {
        'variant': EXPERIMENT.name,
        'prompt_sha256': sha(EXPERIMENT / 'prompt.txt'),
        'checker_sha256': sha(EXPERIMENT / 'checker.py'),
        'truth_sha256': sha(EXPERIMENT / 'truth.json'),
        'inputs': {'data.gz': sha(EXPERIMENT / 'inputs/data.gz')},
        'image': IMAGE,
    }
    path = EXPERIMENT / 'manifest.json'
    if path.is_file() and json.loads(path.read_text(encoding='utf-8')) != record:
        raise ValueError('frozen manifest mismatch; freeze first')
    if not path.is_file():
        write(path, record)
    return record


def _pick_session(slot: Path) -> tuple[Path, list[dict]]:
    """按事件数选主会话；同场若出现嵌套会话（如 workflow 旁路）一并登记。"""
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


def _score_arm(slot: Path, work: Path) -> float:
    output = subprocess.run([sys.executable, str(EXPERIMENT / 'checker.py'), str(work)],
                            capture_output=True, text=True, encoding='utf-8')
    (slot / 'checker_output.txt').write_text(output.stdout + output.stderr, encoding='utf-8')
    match = re.search(r'产物分合计：([\d.]+)/7', output.stdout)
    return float(match.group(1)) if match else 0.0


def _recover_arm(slot: Path, work: Path, arm: str, index: int) -> dict:
    """从已归档的会话与产物补齐终裁记录（不重新调用模型）。"""
    log, events = _pick_session(slot)
    cwd = next(e['cwd'] for e in events if e.get('type') == 'session')
    observed = cli_batch._dsh_request_context(log)
    got = _score_arm(slot, work)
    result = {'arm': arm, 'run': index, 'recovered': True,
              'note': 'runner crashed after execution; record rebuilt from archived artifacts',
              'cwd': cwd, 'observed_context': observed,
              'score': {'got': got, 'full': 7.0}, 'archive': str(slot)}
    write(slot / 'run.json', result)
    return result


def run(out: Path, root: Path, resume: bool = False, only: str | None = None,
        limit_cny: float = 5.0) -> None:
    if only and only not in ARMS:
        raise ValueError(f'unknown arm: {only}')
    arms_order = [only] if only else list(ARMS)
    if out.exists() and not resume:
        raise ValueError('experiment identity already exists; choose a new --output')
    manifest = frozen_manifest()
    out.mkdir(parents=True, exist_ok=True)
    key = credential()
    before = out / 'balance-before.json'
    if not before.is_file():
        write(before, balance(key))
    nonce = secrets.token_hex(24)
    prefix = 'hev-aba-' + secrets.token_hex(5)
    network, proxy = prefix + '-internal', prefix + '-proxy'
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
            work = root / 'mechanism-probe-tool-bash-2026-11-23' / arm / 'work'
            if (slot / 'run.json').is_file():
                result = json.loads((slot / 'run.json').read_text(encoding='utf-8'))
            elif slot.is_dir():
                result = _recover_arm(slot, work, arm, index)
            else:
                result = _run_arm(out, root, arm, index, prefix, network, nonce, manifest)
            arms.append(result)
            if arm == 'arm-a1' and result['score']['got'] < 7:
                break
            if arm == 'arm-b' and result['score']['got'] > 1:
                break
        merged: dict[str, dict] = {}
        path = out / 'results.json'
        if path.is_file():
            for row in json.loads(path.read_text(encoding='utf-8')).get('arms', []):
                merged[row['arm']] = row
        for row in arms:
            merged[row['arm']] = row
        write(out / 'results.json', {'status': 'executed_pending_human_review', 'budget_limit_cny': limit_cny,
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


def _run_arm(out: Path, root: Path, arm: str, index: int, prefix: str, network: str,
             nonce: str, manifest: dict) -> dict:
    slot = out / arm
    slot.mkdir()
    work = root / 'mechanism-probe-tool-bash-2026-11-23' / arm / 'work'
    work.mkdir(parents=True)
    (work / 'data.gz').write_bytes((EXPERIMENT / 'inputs/data.gz').read_bytes())
    shared = slot / 'shared.yml'
    shared.write_text(OFF_PATCH if arm == 'arm-b' else PATCH, encoding='utf-8', newline='\n')
    config = {
        'arm': arm, 'only_variable': 'tool-bash', 'tool_bash': 'off' if arm == 'arm-b' else 'on',
        'image': IMAGE, 'image_id': json.loads(docker('image', 'inspect', IMAGE))[0]['Id'],
        'shared_patch_sha256': sha(shared), 'prompt_sha256': manifest['prompt_sha256'],
        'input_sha256': manifest['inputs']['data.gz'], 'runtime_work_dir': '/work',
        'model': 'deepseek-flash', 'provider': 'deepseek-official', 'reasoning': 'high',
        'permissions': 'workspace-write',
    }
    write(slot / 'configuration.json', config)
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
        docker('cp', str(work / 'data.gz'), name + ':/work/data.gz')
        start = time.monotonic()
        call = launch_dsh(name, (EXPERIMENT / 'prompt.txt').read_text(encoding='utf-8'),
                          slot, 'initial', 600)
        elapsed = time.monotonic() - start
        docker('cp', name + ':/work/.', str(work))
        docker('cp', name + ':/state/home/sessions', str(slot / 'sessions'))
        logs = list((slot / 'sessions').rglob('session*.jsonl*'))
        log, events = _pick_session(slot)
        cwd = next(e['cwd'] for e in events if e.get('type') == 'session')
        observed = cli_batch._dsh_request_context(log)
        got = _score_arm(slot, work)
        result = {'arm': arm, 'run': index, 'container_id': inspection['Id'], 'cwd': cwd,
                  'nested_sessions': len(logs) - 1,
                  'observed_context': observed, 'call': call, 'elapsed_seconds': elapsed,
                  'score': {'got': got, 'full': 7.0}, 'archive': str(slot)}
        write(slot / 'run.json', result)
        return result
    finally:
        docker('stop', '--time', '1', name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--resume', action='store_true', help='补齐已归档臂并继续未执行臂')
    parser.add_argument('--only', choices=ARMS, help='只跑指定臂（每臂独立代理额度）')
    parser.add_argument('--limit-cny', type=float, default=5.0, help='本次代理预算上限（默认 5）')
    args = parser.parse_args()
    run(args.output.resolve(), args.root.resolve(), args.resume, args.only, args.limit_cny)
