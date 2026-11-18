import os,subprocess,json,secrets,pathlib,yaml
base=pathlib.Path(__file__).resolve().parents[1]
runtime=pathlib.Path(os.environ['LAB_RUNTIME']).resolve()
if runtime.is_relative_to(base): raise ValueError('LAB_RUNTIME precisa ficar fora do repo')
runtime.mkdir(mode=0o700,parents=True,exist_ok=True)
runtime.chmod(0o700)
os.umask(0o077)
os.environ['KUBECONFIG']=str(runtime/'admin.config'); os.environ['PATH']=str(pathlib.Path.home()/'.local/bin')+':'+os.environ['PATH']
k=['kubectl','--context','kind-desafio03']
def run(args,**kw):
 r=subprocess.run(k+args,text=True,capture_output=True,**kw)
 if r.returncode: raise RuntimeError(r.stderr)
 return r.stdout
def main():
    with (base/'evidencias/t01/aplicacao.txt').open('w') as log:
     for path in sorted((base/'ticket-01-padrao-de-manifests/manifests').glob('*.yaml')):
      docs=list(yaml.safe_load_all(path.read_text())); ns=docs[0]['metadata']['name']
      log.write(run(['apply','-f','-'],input=yaml.safe_dump(docs[0])))
      secret={'apiVersion':'v1','kind':'Secret','metadata':{'name':'database-auth','namespace':ns},'type':'Opaque','stringData':{'password':secrets.token_hex(24)}}
      log.write(run(['apply','-f','-'],input=yaml.safe_dump(secret)))
      log.write(run(['apply','-f',str(path)]));log.flush()
    print('Aplicação concluída; Secrets efêmeros criados via stdin sem exportar valores.')

if __name__ == '__main__':
    main()
