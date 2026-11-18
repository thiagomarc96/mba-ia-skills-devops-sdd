"""Cliente JSON-RPC stdio: descobre ferramentas e coleta somente leituras reais."""
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'evidencias/t02'

class MCP:
    def __init__(self, config=None):
        env = dict(os.environ)
        if config:
            env['KUBECONFIG_RO'] = config
        self.stderr = open(os.devnull, 'w')
        self.process = subprocess.Popen(['bash', str(Path(__file__).parent/'iniciar.sh')], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.stderr, env=env, text=True, bufsize=1, start_new_session=True)
        self.counter = 0
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.process.stdout, selectors.EVENT_READ)
        self.request('initialize', {'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'desafio03-evidencias','version':'1.0.0'}})
        self.process.stdin.write(json.dumps({'jsonrpc':'2.0','method':'notifications/initialized'})+'\n'); self.process.stdin.flush()

    def request(self, method, params):
        self.counter += 1
        req = {'jsonrpc':'2.0','id':self.counter,'method':method,'params':params}
        start = time.perf_counter()
        self.process.stdin.write(json.dumps(req)+'\n'); self.process.stdin.flush()
        while True:
            if not self.selector.select(timeout=90):
                raise TimeoutError('MCP não respondeu em 90s')
            line = self.process.stdout.readline()
            if not line:
                raise RuntimeError('Servidor MCP encerrou')
            try: response = json.loads(line)
            except ValueError: continue
            if response.get('id') == self.counter:
                return {'request':req, 'response':response, 'segundos':round(time.perf_counter()-start, 4)}

    def close(self):
        os.killpg(self.process.pid, signal.SIGTERM)
        try: self.process.wait(timeout=10)
        except subprocess.TimeoutExpired: os.killpg(self.process.pid, signal.SIGKILL); self.process.wait()
        self.stderr.close(); self.selector.close()

def texts(record):
    return '\n'.join(c.get('text','') for c in record['response'].get('result',{}).get('content',[]))

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    client=MCP()
    try:
        record=client.request('tools/list',{})
        (OUT/'mcp-tools.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
        for ns, app in [('nyx-prod','nyx-api'),('orion-stg','orion-web'),('nyx-stg','nyx-api')]:
            records=[]
            # Listagem JSON é resumida pelo servidor; YAML conserva spec/status da API.
            for resource in ['deployments','pods','services','endpointslices.discovery.k8s.io','events']:
                records.append(client.request('tools/call',{'name':'kubectl_get','arguments':{'resourceType':resource,'name':'','namespace':ns,'output':'yaml'}}))
            (OUT/(ns+'-mcp.json')).write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
            print(ns,'5 consultas reais concluídas',flush=True)
        # Tentativa real de ferramenta não exposta: wrapper/RBAC impedem efeito.
        denial=client.request('tools/call',{'name':'kubectl_create','arguments':{'resourceType':'configmap','name':'escrita-negada','namespace':'nyx-dev'}})
        (OUT/'mcp-escrita-negada.json').write_text(json.dumps(denial,ensure_ascii=False,indent=2)+'\n')
    finally:
        client.close()

if __name__=='__main__':
    main()
