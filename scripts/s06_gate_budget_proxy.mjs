// Ephemeral API-only proxy. Credentials arrive on stdin, never argv or disk.
import http from 'node:http';
import fs from 'node:fs';
import readline from 'node:readline';
const reader = readline.createInterface({input: process.stdin});
const settings = await new Promise(resolve => reader.once('line', line => resolve(JSON.parse(line))));
reader.close();
let reserved = 0, calls = 0;
const log = data => fs.appendFileSync('/state/budget.jsonl', JSON.stringify(data)+'\n');
http.createServer(async (request, response) => {
  if (request.headers['x-api-key'] !== settings.nonce && request.headers.authorization !== 'Bearer '+settings.nonce) {
    response.writeHead(401).end(); return;
  }
  if (request.method !== 'POST' || request.url.split('?')[0] !== '/anthropic/v1/messages') {
    response.writeHead(403).end(); return;
  }
  try {
    const chunks=[]; let bytes=0;
    for await (const chunk of request) {bytes+=chunk.length;if(bytes>2000000)throw Error('body_limit');chunks.push(chunk);}
    const body=Buffer.concat(chunks), data=JSON.parse(body);
    if(data.model !== 'deepseek-flash' || !Number.isInteger(data.max_tokens) || data.max_tokens>8192 || data.max_tokens<1)throw Error('model_or_output_limit');
    // Official peak USD 0.3/1.2 per million; reserve at conservative 8 CNY/USD.
    const reserve=(bytes+4096)*2.4/1e6+data.max_tokens*9.6/1e6;
    if(reserved+reserve>2)throw Error('budget_limit');
    reserved+=reserve;calls++;
    log({event:'reservation',call:calls,input_bytes:bytes,max_output_tokens:data.max_tokens,reserve_cny:reserve,cumulative_reserved_cny:reserved});
    const upstream=await fetch('https://api.deepseek.com'+request.url,{
      method:'POST',headers:{'x-api-key':settings.key,'anthropic-version':request.headers['anthropic-version']||'2023-06-01','content-type':'application/json'},
      body,signal:AbortSignal.timeout(115000)});
    response.writeHead(upstream.status,{'content-type':upstream.headers.get('content-type')||'application/json'});
    const decoder=new TextDecoder();let pending='';
    for await(const chunk of upstream.body){
      response.write(chunk);pending+=decoder.decode(chunk,{stream:true});
      const lines=pending.split('\n');pending=lines.pop();
      for(const line of lines)if(line.startsWith('data: '))try{
        const event=JSON.parse(line.slice(6));const usage=event.usage||event.message?.usage;
        if(usage)log({event:'usage',call:calls,usage});
      }catch{}
    }
    response.end();log({event:'completed',call:calls,http_status:upstream.status});
  }catch(error){log({event:'blocked_or_error',reason:error.message,cumulative_reserved_cny:reserved});if(!response.headersSent)response.writeHead(429,{'content-type':'application/json'});response.end(JSON.stringify({type:'error',error:{type:'rate_limit_error',message:'Experiment proxy stopped request'}}));}
}).listen(9444,'0.0.0.0',()=>{log({event:'ready',limit_cny:2,price_reserve_cny_per_million:{input:2.4,output:9.6}});console.log('READY');});
