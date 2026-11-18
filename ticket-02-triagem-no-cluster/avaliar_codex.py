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
def casos_reais():
    dados = {}
    for ns in ('nyx-prod', 'orion-stg', 'nyx-stg'):
        arquivo = REPO / 'evidencias/t02' / (ns + '-mcp.json')
        records = json.loads(arquivo.read_text())
        partes = []
        for record in records:
            resposta = record['response']
            if 'error' in resposta or resposta.get('result', {}).get('isError'):
                raise RuntimeError('Coleta MCP falhou: ' + ns)
            partes.append({'recurso': record['request']['params']['arguments']['resourceType'],
                           'saida_mcp': resposta['result']})
        dados[ns] = {'origem': str(arquivo.relative_to(REPO)), 'namespace': ns, 'leituras': partes}
    return dados



def executar(item):
    nome, prompt, entrada = item
    env = {**os.environ, 'RUST_LOG': 'error'}
    inicio = time.perf_counter()
    result = subprocess.run([shutil.which('codex'), 'exec', '--ignore-user-config', '--skip-git-repo-check', '--ephemeral', '--sandbox', 'read-only', '--json', '-'], input=prompt, text=True, encoding='utf-8', capture_output=True, cwd=REPO, env=env, timeout=300)
    eventos = []
    for linha in result.stdout.splitlines():
        try:
            eventos.append(json.loads(linha))
        except ValueError:
            pass
    respostas = [e['item']['text'] for e in eventos if e.get('type') == 'item.completed' and e.get('item', {}).get('type') == 'agent_message']
    usos = [e.get('usage') for e in eventos if e.get('type') == 'turn.completed']
    registro = {'entrada': entrada, 'resposta': '\n'.join(respostas), 'segundos': round(time.perf_counter()-inicio, 3), 'usage': usos[-1] if usos else None, 'custo_monetario': None, 'codigo': result.returncode}
    registro['eventos_codex'] = eventos
    registro['stderr'] = result.stderr
    (SAIDA / (nome + '.json')).write_text(json.dumps(registro, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(nome, 'concluído', flush=True)
    if result.returncode or not respostas:
        raise RuntimeError('Execução incompleta: ' + nome)
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
    for nome, caso in casos_reais().items():
        for modo in (['com-skill','sem-skill'] if nome != 'orion-stg' else ['com-skill']):
            contexto = textos[1] if modo == 'com-skill' else ''
            prompt = base + contexto + '\nAnalise o chamado usando estas saídas reais do MCP, coletadas no kind-desafio03. Entregue causa, evidências e próxima ação sugerida, sem executá-la. Seja conciso.\n'+json.dumps(caso,ensure_ascii=False)
            tarefas.append((nome+'-'+modo, prompt, {'caso':caso,'modo':modo}))
    barrado = (REPO/'ticket-01-padrao-de-manifests/exemplos/manifesto-barrado.yaml').read_text()
    for modo in ('com-skill','sem-skill'):
        contexto = textos[0] + '\n' + (paths[0].parent/'references/criterios.md').read_text() if modo == 'com-skill' else ''
        tarefas.append(('manifesto-'+modo, base+contexto+'\nConfira este YAML sem alterá-lo. Indique violações e impacto.\n'+barrado, {'modo':modo,'arquivo':'manifesto-barrado.yaml'}))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        resultados = dict(pool.map(executar,tarefas))
    rotas=[]
    for i, (frase, esperado) in enumerate(FRASES,1):
        dado=resultados[f'rota-{i:02d}']; obtido=dado['resposta'].strip().strip('`')
        rotas.append({'frase':frase,'esperado':esperado,'obtido':obtido,'acerto':obtido==esperado})
    (SAIDA/'roteamento.json').write_text(json.dumps(rotas,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    comparacao=[]
    for nome in ('nyx-prod','nyx-stg','manifesto'):
        comparacao.append({'caso':nome,**{modo:resultados[nome+'-'+modo] for modo in ('com-skill','sem-skill')}})
    (SAIDA/'comparacao.json').write_text(json.dumps(comparacao,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__ == '__main__':
    main()
