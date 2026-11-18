from preparar import base, runtime, run, k
import os, json, yaml, secrets
log=[]
log.append(run(['apply','-f',str(base/'desafio-03/ticket-02-triagem-no-cluster/mcp/rbac.yaml')]))
for ns in ['nyx-dev','nyx-prod','nyx-stg','orion-dev','orion-stg']:
 role={'apiVersion':'rbac.authorization.k8s.io/v1','kind':'RoleBinding','metadata':{'name':'platform-ro','namespace':ns},'roleRef':{'apiGroup':'rbac.authorization.k8s.io','kind':'ClusterRole','name':'view'},'subjects':[{'kind':'ServiceAccount','name':'platform-ro','namespace':'default'}]}
 log.append(run(['apply','-f','-'],input=yaml.safe_dump(role)))
 # Salva RBAC sem credencial.
 (base/f'desafio-03/ticket-02-triagem-no-cluster/mcp/view-{ns}.yaml').write_text(yaml.safe_dump(role,sort_keys=False))
config=yaml.safe_load(run(['config','view','--raw','--minify']))
# A credencial efêmera só existe em arquivo privado fora do Git.
token=run(['-n','default','create','token','platform-ro','--duration=1h']).strip()
config['users']=[{'name':'platform-ro','user':{'token':token}}]
config['contexts'][0]['context']['user']='platform-ro'
for name, obj in [('ro.config',config),('unavailable.config',json.loads(json.dumps(config)))]:
 if name=='unavailable.config': obj['clusters'][0]['cluster']['server']='https://127.0.0.1:9'
 p=runtime/name; p.write_text(yaml.safe_dump(obj));p.chmod(0o600)
# Token ligado ao Secret: revogação ocorre ao remover o objeto de vínculo.
log.append(run(['-n','default','create','serviceaccount','platform-expired']))
log.append(run(['-n','default','create','secret','generic','token-anchor']))
expired=run(['-n','default','create','token','platform-expired','--duration=1h','--bound-object-kind','Secret','--bound-object-name','token-anchor']).strip()
config['users'][0]['user']['token']=expired
p=runtime/'revoked.config';p.write_text(yaml.safe_dump(config));p.chmod(0o600)
log.append(run(['-n','default','delete','secret','token-anchor']))
(base/'evidencias/t02/rbac-preparo.txt').write_text(''.join(log))
print('RBAC view/platform-ro pronto; três kubeconfigs privados fora do repo.')
