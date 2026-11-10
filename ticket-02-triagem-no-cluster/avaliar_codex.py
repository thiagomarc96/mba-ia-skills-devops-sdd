"""Avaliação das skills com entradas de exemplo e sessões independentes do Codex."""
import concurrent.futures
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
SAIDA = ROOT / 'exemplos'
FRASES = [
    ('o pod do nyx-prod não sobe', 'triagem-cluster'),
    ('por que esse deployment está 0/3', 'triagem-cluster'),
    ('o service do nyx-stg não tem endpoint', 'triagem-cluster'),
    ('revisa esse deployment antes de eu subir', 'manifests-metacortex'),
    ('esse manifesto está no padrão da casa?', 'manifests-metacortex'),
    ('cria um Deployment novo do zero pra mim', 'manifests-metacortex'),
    ('esse manifesto não sobe no cluster', 'esclarecer'),
    ('o Service do nyx não está entregando tráfego', 'triagem-cluster'),
    ('o que é um DaemonSet?', 'nenhuma'),
    ('provisiona uma VM nova no Construct pro cliente orion', 'nenhuma'),
]
CASOS = {
 'nyx-prod': {'sintoma': 'API reinicia', 'pod': {'phase': 'Running', 'restartCount': 17, 'lastState': {'terminated': {'reason': 'OOMKilled', 'exitCode': 137}}, 'state': {'waiting': {'reason': 'CrashLoopBackOff'}}, 'memory_limit': '24Mi'}, 'eventos': ['Back-off restarting failed container api'], 'postgres': {'ready': True, 'restartCount': 0}},
 'orion-stg': {'sintoma': 'Loja parou após publicação', 'deployment': {'readyReplicas': 0, 'replicas': 3, 'image': 'fabricioveronez/fake-shop:v1.14.2'}, 'pod': {'state': 'ImagePullBackOff'}, 'eventos': ['Failed to pull image: manifest unknown'], 'postgres': {'ready': True}},
 'nyx-stg': {'sintoma': 'Service não entrega tráfego', 'service': {'selector': {'app': 'nyx-api'}}, 'pods': [{'labels': {'app': 'nyxapi'}, 'ready': True, 'restartCount': 0}], 'endpointslices': [], 'postgres': {'ready': True}},
}


def executar(item):
    nome, prompt, entrada = item
    env = {**os.environ, 'RUST_LOG': 'error'}
    inicio = time.perf_counter()
    result = subprocess.run([shutil.which('codex'), 'exec', '--ephemeral', '--sandbox', 'read-only', '--json', '-'], input=prompt, text=True, encoding='utf-8', capture_output=True, cwd=REPO, env=env, timeout=180)
    eventos = []
    for linha in result.stdout.splitlines():
        try:
            eventos.append(json.loads(linha))
        except ValueError:
            pass
    respostas = [e['item']['text'] for e in eventos if e.get('type') == 'item.completed' and e.get('item', {}).get('type') == 'agent_message']
    usos = [e.get('usage') for e in eventos if e.get('type') == 'turn.completed']
    registro = {'entrada': entrada, 'resposta': '\n'.join(respostas), 'segundos': round(time.perf_counter()-inicio, 3), 'usage': usos[-1] if usos else None, 'custo_monetario': None, 'codigo': result.returncode}
    if result.returncode or not respostas:
        raise RuntimeError('Execução incompleta: ' + nome)
    (SAIDA / (nome + '.json')).write_text(json.dumps(registro, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(nome, 'concluído', flush=True)
    return nome, registro


def main():
    SAIDA.mkdir(exist_ok=True)
    paths = [REPO/'ticket-01-padrao-de-manifests/skill/SKILL.md', ROOT/'skill/SKILL.md']
    textos = [p.read_text(encoding='utf-8') for p in paths]
    catalogo = '\n'.join(t.split('---')[1] for t in textos)
    base = 'Não use ferramentas nem consulte arquivos/rede. Trabalhe apenas com os dados fornecidos. Responda em português, sem inventar acesso a cluster.\n'
    tarefas=[]
    for i, (frase, esperado) in enumerate(FRASES, 1):
        prompt = base + 'Escolha a rota entre manifests-metacortex, triagem-cluster, esclarecer, nenhuma. Responda apenas com o nome da rota. Catálogo:\n'+catalogo+'\nPedido: '+frase
        tarefas.append((f'rota-{i:02d}', prompt, {'frase':frase,'esperado':esperado,'catalogo':'descrições das duas skills'}))
    for nome, caso in CASOS.items():
        for modo in (['com-skill','sem-skill'] if nome != 'orion-stg' else ['com-skill']):
            contexto = textos[1] if modo == 'com-skill' else ''
            prompt = base + contexto + '\nAnalise o chamado usando este conjunto de dados de exemplo. Entregue causa, evidências e próxima ação sugerida, sem executá-la. Seja conciso.\n'+json.dumps(caso,ensure_ascii=False)
            tarefas.append((nome+'-'+modo, prompt, {'caso':caso,'modo':modo}))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        resultados = dict(pool.map(executar,tarefas))
    rotas=[]
    for i, (frase, esperado) in enumerate(FRASES,1):
        dado=resultados[f'rota-{i:02d}']; obtido=dado['resposta'].strip().strip('`')
        rotas.append({'frase':frase,'esperado':esperado,'obtido':obtido,'acerto':obtido==esperado})
    (SAIDA/'roteamento.json').write_text(json.dumps(rotas,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    comparacao=[]
    for nome in ('nyx-prod','nyx-stg'):
        comparacao.append({'caso':nome,**{modo:resultados[nome+'-'+modo] for modo in ('com-skill','sem-skill')}})
    (SAIDA/'comparacao.json').write_text(json.dumps(comparacao,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__ == '__main__':
    main()
