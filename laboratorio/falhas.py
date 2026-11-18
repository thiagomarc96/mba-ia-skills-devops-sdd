import os,sys,json,pathlib,ssl,base64,urllib.request,urllib.error,re,subprocess,yaml
from preparar import base, runtime
sys.path.insert(0,str(base/'ticket-02-triagem-no-cluster/mcp'))
from coletar import MCP
out=base/'evidencias/t04'
os.environ['PATH']=str(pathlib.Path.home()/'.local/bin')+':'+os.environ['PATH']
records=[]
for nome,config,path in [('credencial-expirada','revoked.config','/api/v1/namespaces/nyx-dev/pods'),('permissao-negada','ro.config','/apis/discovery.k8s.io/v1/namespaces/acesso-parcial/endpointslices'),('cluster-indisponivel','unavailable.config','/api/v1/namespaces/nyx-dev/pods')]:
 conf=yaml.safe_load((runtime/config).read_text());cluster=conf['clusters'][0]['cluster'];token=conf['users'][0]['user']['token']
 ca=ssl.create_default_context(cadata=base64.b64decode(cluster['certificate-authority-data']).decode())
 url=cluster['server']+path
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'Authorization':'Bearer '+token}),context=ca,timeout=3) as resp:
   status=resp.status;body=resp.read().decode()
 except urllib.error.HTTPError as e: status=e.code;body=e.read().decode()
 except urllib.error.URLError: status=None;body='Conexão recusada na porta inválida do kubeconfig isolado.'
 records.append({'cenario':nome,'server':'[MASCARADO]','certificados':'[MASCARADOS]','path':path,'http_status':status,'resposta':json.loads(body) if status else body})
 client=MCP(str(runtime/config))
 try:
  r=client.request('tools/call',{'name':'kubectl_get','arguments':{'resourceType':'endpointslices.discovery.k8s.io' if nome=='permissao-negada' else 'pods','name':'','namespace':'acesso-parcial' if nome=='permissao-negada' else 'nyx-dev','output':'yaml'}})
  texto=json.dumps(r,ensure_ascii=False,indent=2).replace(cluster['server'],'https://[SERVER_MASCARADO]')
  texto=texto.replace('127.0.0.1:9','[SERVER_MASCARADO]')
  texto=re.sub(r'https?://(?:127\.0\.0\.1|localhost):\d+', 'https://[SERVER_MASCARADO]',texto)
  (out/(nome+'-mcp.json')).write_text(texto+'\n')
 finally:client.close()
(out/'falhas-http.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
assert [r['http_status'] for r in records]==[401,403,None]
print('Falhas reais confirmadas: 401, 403 e conexão recusada; consultas MCP registradas.')
