"""No upstream calls: test proxy rejection and reservation failure in an offline container."""
import json
import os
import secrets
import subprocess
import time
from pathlib import Path

import pytest


@pytest.mark.skipif(os.environ.get('HEV_DOCKER_TESTS') != '1', reason='explicit offline Docker integration test')
def test_proxy_blocks_unapproved_routes_models_and_budget_even_after_upstream_failure(tmp_path):
    name='hev-proxy-test-'+secrets.token_hex(5)
    def docker(*args, **kwargs):
        return subprocess.run(['docker',*args],check=True,capture_output=True,text=True,encoding='utf-8',**kwargs).stdout
    docker('run','-d','--name',name,'--network','none','harness-p0-dsh:20261120','sleep','infinity')
    docker('cp',str(Path(__file__).resolve().parents[2]/'scripts/p0_budget_proxy.mjs'),name+':/control/proxy.mjs')
    process=subprocess.Popen(['docker','exec','-i',name,'node','/control/proxy.mjs'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    process.stdin.write(json.dumps({'key':'offline-not-a-real-key','nonce':'unit-nonce'})+'\n')
    process.stdin.flush();process.stdin.close()
    try:
        ready=False
        for _ in range(50):
            probe=docker('exec',name,'sh','-c','test -s /state/budget.jsonl && echo ready || true')
            if 'ready' in probe:ready=True;break
            time.sleep(.1)
        assert ready
        client="""const call=async(path,method,key,data)=>{const r=await fetch('http://127.0.0.1:9444'+path,{method,headers:{'x-api-key':key,'content-type':'application/json'},...data?{body:JSON.stringify(data)}:{}});await r.text();return r.status;};const result=[];result.push(await call('/anthropic/v1/messages','POST','wrong',{model:'deepseek-flash',max_tokens:1}));result.push(await call('/models','GET','unit-nonce'));result.push(await call('/anthropic/v1/messages','POST','unit-nonce',{model:'other-model',max_tokens:1}));result.push(await call('/anthropic/v1/messages','POST','unit-nonce',{model:'deepseek-flash',max_tokens:8193}));const large={model:'deepseek-flash',max_tokens:8192,messages:[{role:'user',content:'x'.repeat(1900000)}]};result.push(await call('/anthropic/v1/messages','POST','unit-nonce',large));result.push(await call('/anthropic/v1/messages','POST','unit-nonce',large));console.log(JSON.stringify(result));"""
        statuses=json.loads(docker('exec',name,'node','-e',client))
        assert statuses == [401,403,429,429,429,429]
        logs=[json.loads(line) for line in docker('exec',name,'cat','/state/budget.jsonl').splitlines()]
        reservations=[row for row in logs if row['event']=='reservation']
        assert len(reservations)==1
        assert reservations[0]['cumulative_reserved_cny'] < 5
        assert any(row.get('reason')=='budget_limit' for row in logs)
    finally:
        docker('stop','--time','1',name)
        process.wait(timeout=20)
        # Remove only the container created by this test; no historical evidence.
        docker('rm',name)


@pytest.mark.skipif(os.environ.get('HEV_DOCKER_TESTS') != '1', reason='explicit offline Docker integration test')
def test_followup_proxy_counts_original_reservation_before_forwarding(tmp_path):
    name='hev-followup-proxy-test-'+secrets.token_hex(5)
    def docker(*args):
        return subprocess.run(['docker',*args],check=True,capture_output=True,text=True,encoding='utf-8').stdout
    docker('run','-d','--name',name,'--network','none','harness-p0-dsh:20261120','sleep','infinity')
    docker('cp',str(Path(__file__).resolve().parents[2]/'scripts/p0_budget_proxy_followup.mjs'),name+':/control/proxy.mjs')
    process=subprocess.Popen(['docker','exec','-i',name,'node','/control/proxy.mjs'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    process.stdin.write(json.dumps({'key':'offline-not-a-real-key','nonce':'unit-nonce','carryoverReservedCny':1.57044})+'\n')
    process.stdin.flush();process.stdin.close()
    try:
        for _ in range(50):
            if 'ready' in docker('exec',name,'sh','-c','test -s /state/budget.jsonl && echo ready || true'):
                break
            time.sleep(.1)
        else:
            pytest.fail('follow-up proxy did not start')
        client="""const body={model:'deepseek-flash',max_tokens:8192,messages:[{role:'user',content:'x'.repeat(1900000)}]};const r=await fetch('http://127.0.0.1:9444/anthropic/v1/messages',{method:'POST',headers:{'x-api-key':'unit-nonce','content-type':'application/json'},body:JSON.stringify(body)});await r.text();console.log(r.status);"""
        assert docker('exec',name,'node','-e',client).strip()=='429'
        logs=[json.loads(line) for line in docker('exec',name,'cat','/state/budget.jsonl').splitlines()]
        assert logs[0]['carryover_reserved_cny']==1.57044
        assert not any(row['event']=='reservation' for row in logs)
        assert any(row.get('reason')=='budget_limit' and row['cumulative_reserved_cny']==1.57044 for row in logs)
    finally:
        docker('stop','--time','1',name)
        process.wait(timeout=20)
        docker('rm',name)
