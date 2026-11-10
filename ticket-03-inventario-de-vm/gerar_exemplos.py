"""Gera exemplos reproduzíveis a partir das fixtures."""
import contextlib
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import yaml
import inventario as app

RAIZ = Path(__file__).resolve().parent


def cenarios():
    conforme = json.loads((RAIZ / 'fixtures' / 'inventario.json').read_text(encoding='utf-8'))
    desvio = copy.deepcopy(conforme)
    inv = desvio['inventario']
    inv['kernel']['versao'] = '5.15.0-118-generic'
    inv['swap'] = {'habilitado': True, 'tamanho': 4294967296, 'unidade': 'bytes'}
    inv['servicos'] = [s for s in inv['servicos'] if s['nome'] != 'chrony.service']
    inv['portas_em_escuta'][1]['bind'] = '0.0.0.0'
    inv['ntp'] = {'sincronizado': False, 'mecanismo': 'não identificado'}
    parcial = copy.deepcopy(conforme)
    parcial['inventario']['ssh'] = None
    parcial['inventario']['cobertura_chaves_ssh'] = 'parcial'
    parcial['erros'] = {'ssh': 'consulta exige privilégio não concedido', 'chaves_ssh': 'cobertura parcial: arquivo inacessível'}
    repeticao = copy.deepcopy(desvio)
    repeticao['host']['coletado_em'] = '2026-11-10T12:01:00Z'
    return {'conforme': (conforme, 0), 'desvio': (desvio, 1), 'parcial': (parcial, 2), 'repeticao': (repeticao, 1)}


def falha_inacessivel():
    erro = io.StringIO()
    # Execute the actual CLI and SSH error mapping, but intercept subprocess.run.
    argv = ['inventario.py', '--host', '192.0.2.10', '--usuario', 'operador', '--chave', 'chave-fixture', '--baseline', str(RAIZ / 'baseline.yaml')]
    retorno = subprocess.CompletedProcess([], 255, '', 'ssh: connect to host 192.0.2.10 port 22: Connection refused')
    with patch.object(sys, 'argv', argv), patch.object(Path, 'is_file', return_value=True), patch.object(app.subprocess, 'run', return_value=retorno) as chamada, contextlib.redirect_stderr(erro):
        codigo = app.main()
    if chamada.call_count != 1 or codigo != 3:
        raise RuntimeError('a falha de conexão não produziu o retorno esperado')
    return {'origem': 'fixture', 'cenario': 'host_inacessivel', 'codigo_saida': codigo, 'erro': erro.getvalue().strip(), 'relatorio_conformidade': None}


def gerar(destino=None):
    destino = Path(destino) if destino is not None else RAIZ / 'exemplos'
    destino.mkdir(parents=True, exist_ok=True)
    baseline = yaml.safe_load((RAIZ / 'baseline.yaml').read_text(encoding='utf-8'))
    resultados = {}
    for nome, (fixture, esperado) in cenarios().items():
        relatorio = app.avaliar(fixture, baseline)
        codigo = app.codigo(relatorio)
        if codigo != esperado:
            raise RuntimeError(f'código inesperado para {nome}')
        resultados[nome] = relatorio
        (destino / f'{nome}.json').write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (destino / f'{nome}.md').write_text(app.markdown(relatorio), encoding='utf-8')
        (destino / f'{nome}.codigo.txt').write_text(f'{codigo}\n', encoding='utf-8')
    a, b = copy.deepcopy(resultados['desvio']), copy.deepcopy(resultados['repeticao'])
    a['host'].pop('coletado_em')
    b['host'].pop('coletado_em')
    if a != b:
        raise RuntimeError('a repetição divergiu além do instante de coleta')
    falha = falha_inacessivel()
    (destino / 'host-inacessivel.json').write_text(json.dumps(falha, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (destino / 'host-inacessivel.md').write_text('# Exemplo — host inacessível\n\n' + falha['erro'] + '\n\nCódigo de saída: 3. Nenhum relatório de conformidade emitido.\n', encoding='utf-8')
    (destino / 'host-inacessivel.codigo.txt').write_text('3\n', encoding='utf-8')
    return resultados


if __name__ == '__main__':
    gerar()
    print('Cinco exemplos gerados: conforme=0, desvio=1, parcial=2, repetição=1, host inacessível=3.')
