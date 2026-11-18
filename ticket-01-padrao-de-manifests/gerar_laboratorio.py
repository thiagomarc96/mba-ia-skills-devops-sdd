from pathlib import Path
import yaml,json,subprocess
root=Path(__file__).resolve().parent.parent
out=root/'ticket-01-padrao-de-manifests/manifests'
def labels(name,ns): return {'app':name,**{'app.kubernetes.io/'+k:v for k,v in {'name':name,'instance':ns,'part-of':ns.rsplit('-',1)[0],'managed-by':'platform'}.items()}}
def meta(name,ns): return {'name':name,'namespace':ns,'labels':labels(name,ns)}
def generate(ns,shop=False):
 app='orion-web' if shop else 'nyx-api'; port=5000 if shop else 8080
 objs=[{'apiVersion':'v1','kind':'Namespace','metadata':{'name':ns,'labels':labels(ns,ns)}}]
 for name in [app,'postgres']:
  objs.append({'apiVersion':'v1','kind':'ServiceAccount','metadata':meta(name,ns),'automountServiceAccountToken':False})
  db=name=='postgres'
  image='postgres:16.6-alpine' if db else ('fabricioveronez/fake-shop@sha256:07db4334f5f2bb330f0f342a81ad203bb21b770b8d7a27c90edb2261fea34e2f' if shop else 'fabricioveronez/kube-news@sha256:61a97024792d8aa96d97d2618b98924012daeaa6386e2557660cc6ff169d840e')
  c={'name':name,'image':image,'imagePullPolicy':'IfNotPresent','ports':[{'name':'db' if db else 'http','containerPort':5432 if db else port}], 'resources':{'requests':{'cpu':'50m','memory':'64Mi' if db else '128Mi'},'limits':{'cpu':'500m','memory':'256Mi'}},'securityContext':{'runAsNonRoot':True,'runAsUser':10001,'runAsGroup':10001,'allowPrivilegeEscalation':False,'readOnlyRootFilesystem':True,'capabilities':{'drop':['ALL']}},'env':[],'volumeMounts':[{'name':'tmp','mountPath':'/tmp'}]}
  if db:
   env={'POSTGRES_DB':'app','POSTGRES_USER':'app','PGDATA':'/var/lib/postgresql/data/pgdata'}
   c['env']=[{'name':k,'value':v} for k,v in env.items()]+[{'name':'POSTGRES_PASSWORD','valueFrom':{'secretKeyRef':{'name':'database-auth','key':'password'}}}]
   c['volumeMounts']+=[{'name':'data','mountPath':'/var/lib/postgresql/data'},{'name':'run','mountPath':'/var/run/postgresql'}]
   ready={'exec':{'command':['pg_isready','-U','app','-d','app']},'periodSeconds':3}
   live=ready.copy()
  else:
   env={'DB_HOST':'postgres','DB_PORT':'5432',('DB_NAME' if shop else 'DB_DATABASE'):'app',('DB_USER' if shop else 'DB_USERNAME'):'app'}
   c['env']=[{'name':k,'value':v} for k,v in env.items()]+[{'name':'DB_PASSWORD','valueFrom':{'secretKeyRef':{'name':'database-auth','key':'password'}}}]
   if shop:
    # O código oferece / mas não /health: prontidão funcional, liveness de socket.
    ready={'httpGet':{'path':'/','port':'http'},'periodSeconds':5}
    live={'tcpSocket':{'port':'http'},'periodSeconds':10}
    c['env']+=[{'name':'PROMETHEUS_MULTIPROC_DIR','value':'/tmp'}]
   else:
    ready={'httpGet':{'path':'/ready','port':'http'},'periodSeconds':5}
    live={'httpGet':{'path':'/health','port':'http'},'periodSeconds':10}
  c['readinessProbe']=ready;c['livenessProbe']=live;c['startupProbe']={**live,'periodSeconds':2,'failureThreshold':60}
  ps={'serviceAccountName':name,'automountServiceAccountToken':False,'terminationGracePeriodSeconds':30,'securityContext':{'fsGroup':10001,'seccompProfile':{'type':'RuntimeDefault'}},'containers':[c],'volumes':[{'name':v,'emptyDir':{}} for v in (['tmp','data','run'] if db else ['tmp'])]}
  if not db:
   ps['initContainers']=[{'name':'aguardar-postgres','image':'postgres:16.6-alpine','command':['sh','-c','until pg_isready -h postgres -U app -d app; do sleep 2; done'],'resources':{'requests':{'cpu':'10m','memory':'16Mi'},'limits':{'cpu':'100m','memory':'64Mi'}},'securityContext':c['securityContext']}]
  spec={'replicas':2 if ns.endswith('-prod') and not db else 1,'selector':{'matchLabels':{'app':name}},'template':{'metadata':{'labels':labels(name,ns)},'spec':ps},'strategy':{'type':'RollingUpdate','rollingUpdate':{'maxUnavailable':0,'maxSurge':1}}}
  objs.append({'apiVersion':'apps/v1','kind':'Deployment','metadata':meta(name,ns),'spec':spec})
  objs.append({'apiVersion':'v1','kind':'Service','metadata':meta(name,ns),'spec':{'selector':{'app':name},'ports':[{'name':'db' if db else 'http','port':5432 if db else 80,'targetPort':'db' if db else 'http'}]}})
 return objs
for ns,shop in [('nyx-dev',False),('orion-dev',True),('nyx-prod',False),('orion-stg',True),('nyx-stg',False)]:
 filename='nyx-api.yaml' if ns=='nyx-prod' else ns+'.yaml'
 (out/filename).write_text(yaml.safe_dump_all(generate(ns,shop),sort_keys=False))
print('5 namespaces, 2 projetos; credencial externa por secretKeyRef; nenhuma senha gerada neste passo.')
