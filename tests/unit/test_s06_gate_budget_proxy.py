"""Offline guard check for the new ¥2 proxy; no upstream model request."""
import json
import os
import secrets
import subprocess
import time
from pathlib import Path

import pytest


@pytest.mark.skipif(os.environ.get('HEV_DOCKER_TESTS') != '1', reason='explicit offline Docker integration test')
def test_s06_proxy_rejects_over_budget_before_forwarding():
    name = 'hev-s06-proxy-test-' + secrets.token_hex(5)

    def docker(*args):
        return subprocess.run(['docker', *args], check=True, capture_output=True,
                              text=True, encoding='utf-8').stdout

    docker('run', '-d', '--name', name, '--network', 'none',
           'harness-p0-dsh:20261120', 'sleep', 'infinity')
    docker('cp', str(Path(__file__).resolve().parents[2] / 'scripts/s06_gate_budget_proxy.mjs'),
           name + ':/control/proxy.mjs')
    process = subprocess.Popen(['docker', 'exec', '-i', name, 'node', '/control/proxy.mjs'],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True)
    process.stdin.write(json.dumps({'key': 'offline-only', 'nonce': 'unit-nonce'}) + '\n')
    process.stdin.flush()
    process.stdin.close()
    try:
        for _ in range(50):
            if 'ready' in docker('exec', name, 'sh', '-c',
                                 'test -s /state/budget.jsonl && echo ready || true'):
                break
            time.sleep(.1)
        else:
            raise AssertionError('proxy did not start')
        client = """const body={model:'deepseek-flash',max_tokens:8192,messages:[{role:'user',content:'x'.repeat(900000)}]};const r=await fetch('http://127.0.0.1:9444/anthropic/v1/messages',{method:'POST',headers:{'x-api-key':'unit-nonce','content-type':'application/json'},body:JSON.stringify(body)});await r.text();console.log(r.status);"""
        assert docker('exec', name, 'node', '-e', client).strip() == '429'
        events = [json.loads(line) for line in docker('exec', name, 'cat',
                                                     '/state/budget.jsonl').splitlines()]
        assert events[0]['limit_cny'] == 2
        assert not any(event['event'] == 'reservation' for event in events)
        assert any(event.get('reason') == 'budget_limit' for event in events)
    finally:
        docker('stop', '--time', '1', name)
        process.wait(timeout=20)
        docker('rm', name)
