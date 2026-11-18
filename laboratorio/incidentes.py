from preparar import base, runtime, run, k
import os, json, yaml, secrets
log=[]
log.append(run(['-n','nyx-prod','set','resources','deployment/nyx-api','--containers=nyx-api','--requests=cpu=50m,memory=16Mi','--limits=cpu=500m,memory=24Mi']))
log.append(run(['-n','orion-stg','set','image','deployment/orion-web','orion-web=fabricioveronez/fake-shop:v1.14.2']))
log.append(run(['-n','orion-stg','scale','deployment/orion-web','--replicas=3']))
# Recriar somente o Deployment do lab permite o selector solicitado, que é imutável.
docs=list(yaml.safe_load_all((base/'desafio-03/ticket-01-padrao-de-manifests/manifests/nyx-stg.yaml').read_text()))
app=next(d for d in docs if d['kind']=='Deployment' and d['metadata']['name']=='nyx-api')
app['spec']['selector']['matchLabels']['app']='nyxapi'
app['spec']['template']['metadata']['labels']['app']='nyxapi'
log.append(run(['-n','nyx-stg','delete','deployment','nyx-api','--wait=true']))
log.append(run(['apply','-f','-'],input=yaml.safe_dump(app)))
# Namespace com leitura parcial para o oitavo cenário do dashboard.
log.append(run(['create','namespace','acesso-parcial']))
for d in docs:
 if d['kind']=='Namespace': continue
 d['metadata']['namespace']='acesso-parcial'
 if d['kind']=='Deployment' and d['metadata']['name']=='nyx-api':
  d['spec']['selector']['matchLabels']['app']='nyx-api';d['spec']['template']['metadata']['labels']['app']='nyx-api'
 log.append(run(['apply','-f','-'],input=yaml.safe_dump(d)))
# Segredo separado gerado na memória.
s={'apiVersion':'v1','kind':'Secret','metadata':{'name':'database-auth','namespace':'acesso-parcial'},'stringData':{'password':secrets.token_hex(24)}}
log.append(run(['apply','-f','-'],input=yaml.safe_dump(s)))
role={'apiVersion':'rbac.authorization.k8s.io/v1','kind':'Role','metadata':{'name':'platform-ro','namespace':'acesso-parcial'},'rules':[{'apiGroups':['','apps'],'resources':['pods','pods/log','services','events','deployments'],'verbs':['get','list','watch']}]}
binding={'apiVersion':'rbac.authorization.k8s.io/v1','kind':'RoleBinding','metadata':{'name':'platform-ro','namespace':'acesso-parcial'},'roleRef':{'apiGroup':'rbac.authorization.k8s.io','kind':'Role','name':'platform-ro'},'subjects':[{'kind':'ServiceAccount','name':'platform-ro','namespace':'default'}]}
for d in [role,binding]:log.append(run(['apply','-f','-'],input=yaml.safe_dump(d)))
(base/'desafio-03/ticket-02-triagem-no-cluster/mcp/acesso-parcial.yaml').write_text(yaml.safe_dump_all([role,binding],sort_keys=False))
(base/'evidencias/t02/injecao-chamados.txt').write_text(''.join(log))
print('3 chamados e acesso parcial preparados no kind-desafio03.')
