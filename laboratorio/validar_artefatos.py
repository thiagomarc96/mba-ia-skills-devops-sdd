"""Confere contratos das evidências, links e caminhos após a organização dos tickets."""
import importlib.util
import json
from pathlib import Path
import re
from urllib.parse import unquote

RAIZ = Path(__file__).resolve().parents[1]
DESAFIO = RAIZ / 'desafio-03'


def ler(caminho):
    return json.loads(caminho.read_text(encoding='utf-8'))


def main():
    for documento in RAIZ.rglob('*.md'):
        if '.git' in documento.parts:
            continue
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', documento.read_text(encoding='utf-8')):
            if re.match(r'^[a-z]+:|^#', link):
                continue
            destino = documento.parent / unquote(link.split('#')[0])
            if not destino.exists():
                raise ValueError(f'Link inexistente em {documento.relative_to(RAIZ)}: {link}')
    for skill in DESAFIO.glob('*/skill/SKILL.md'):
        if skill.stat().st_size > 4096:
            raise ValueError('Skill sem a margem mínima de 20%: ' + str(skill.relative_to(RAIZ)))
    config = ler(DESAFIO / 'ticket-02-triagem-no-cluster/mcp/config.json')
    for servidor in config['mcpServers'].values():
        if not (RAIZ / servidor['args'][0]).is_file():
            raise ValueError('Launcher MCP inexistente')
    t02 = DESAFIO / 'ticket-02-triagem-no-cluster/exemplos'
    comparacao = ler(t02 / 'comparacao.json')
    if {c['caso'] for c in comparacao} != {'nyx-prod', 'orion-stg', 'nyx-stg', 'manifesto'}:
        raise ValueError('Comparativo incompleto')
    for caso in comparacao:
        for modo in ('com-skill', 'sem-skill'):
            registro = caso[modo]
            if registro != ler(t02 / f"{caso['caso']}-{modo}.json"):
                raise ValueError('Comparativo diverge do registro individual')
            if registro['codigo'] or not registro['resposta'] or not registro['usage'] or registro['segundos'] <= 0:
                raise ValueError('Execução de modelo incompleta')
    rotas = ler(t02 / 'roteamento.json')
    if len(rotas) != 10 or not all(x['acerto'] for x in rotas):
        raise ValueError('Roteamento divergente')
    spec = importlib.util.spec_from_file_location('inventario', DESAFIO / 'ticket-03-inventario-de-vm/inventario.py')
    inventario = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inventario)
    pasta = RAIZ / 'evidencias/t03'
    coletas = []
    for nome in ('primeira', 'segunda'):
        relatorio = ler(pasta / nome / 'inventario.json')
        if (pasta / nome / 'inventario.md').read_text() != inventario.markdown(relatorio):
            raise ValueError('JSON e Markdown de inventário divergem')
        if int((pasta / f'{nome}.codigo.txt').read_text()) != inventario.codigo(relatorio):
            raise ValueError('Código de retorno diverge do inventário')
        coletas.append(relatorio)
    if coletas[0]['host']['coletado_em'] == coletas[1]['host']['coletado_em'] or coletas[0]['conformidade'] != coletas[1]['conformidade']:
        raise ValueError('Repetição não confirma instantes distintos e vereditos iguais')
    falha = ler(pasta / 'host-inacessivel.json')
    if falha['codigo_saida'] != 3 or not falha['erro_tcp'] or falha['relatorio_conformidade'] is not None:
        raise ValueError('Host inacessível sem comprovação de falha')
    print('Links locais, caminhos MCP, margem das skills, 10 rotas, 4 comparativos e contratos SSH: OK.')


if __name__ == '__main__':
    main()
