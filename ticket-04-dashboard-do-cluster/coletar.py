"""Coleta evidências HTTP do Kubernetes real; somente get no contexto autorizado."""
import argparse
import json
import os
from http.server import HTTPServer
from pathlib import Path
from threading import Thread
from urllib.request import urlopen
from dashboard import Kubernetes, handler_for

CASOS = {
    'nyx-dev': ('nyx-dev', 'KUBECONFIG_RO'),
    'orion-dev': ('orion-dev', 'KUBECONFIG_RO'),
    'nyx-prod': ('nyx-prod', 'KUBECONFIG_RO'),
    'orion-stg': ('orion-stg', 'KUBECONFIG_RO'),
    'nyx-stg': ('nyx-stg', 'KUBECONFIG_RO'),
    'acesso-parcial': ('acesso-parcial', 'KUBECONFIG_RO'),
    'credencial-expirada': ('nyx-dev', 'KUBECONFIG_REVOGADO'),
    'cluster-indisponivel': ('nyx-dev', 'KUBECONFIG_INDISPONIVEL'),
}

class Coleta(Kubernetes):
    def __init__(self):
        super().__init__(context='kind-desafio03')
        self.consultas = []
        self.entradas = {}

    def get(self, resource, namespace=None):
        self.consultas.append({'recurso': resource, 'namespace': namespace})
        data = super().get(resource, namespace)
        self.entradas[resource] = data
        return data

def coletar(nome, namespace, config):
    os.environ['KUBECONFIG'] = config
    client = Coleta()
    server = HTTPServer(('127.0.0.1', 0), handler_for(client))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f'http://127.0.0.1:{server.server_port}'
        with urlopen(base + '/api/estado?namespace=' + namespace, timeout=90) as response:
            status, result = response.status, json.load(response)
        assert status == 200
        if nome in ('nyx-dev', 'orion-dev'):
            assert not result['erros'] and all(p['pronto'] for p in result['pods']) and len(result['pods']) >= 2
        elif nome == 'nyx-prod':
            assert any('OOMKilled' in p['motivo'] for p in result['pods'])
        elif nome == 'orion-stg':
            assert any('ImagePull' in p['motivo'] for p in result['pods'])
        elif nome == 'nyx-stg':
            assert any(s['nome'] == 'nyx-api' and s['endpoints'] == 'Sem endpoint pronto' for s in result['services'])
            assert all(p['pronto'] for p in result['pods'])
        elif nome == 'acesso-parcial':
            assert 'endpointslices.discovery.k8s.io' in result['erros'] and result['pods']
        else:
            assert len(result['erros']) == 6 and not result['pods']
            expected = 'Autenticação' if nome == 'credencial-expirada' else 'Cluster indisponível'
            assert all(expected in e for e in result['erros'].values())
        for path in ('/', '/app.js', '/style.css'):
            with urlopen(base + path) as response:
                assert response.status == 200 and response.read()
        return {'origem': 'API do kind-desafio03 via kubectl e backend HTTP', 'cenario': nome,
                'http_status': status, 'entrada_cluster': client.entradas,
                'consultas': client.consultas, 'resposta': result}
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=5)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cenario', choices=CASOS)
    args = parser.parse_args()
    directory = Path(__file__).parent / 'exemplos/fixtures'
    summary = []
    for nome, (namespace, variable) in CASOS.items():
        if args.cenario and nome != args.cenario:
            continue
        config = os.environ[variable]
        record = coletar(nome, namespace, config)
        (directory / (nome+'.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
        summary.append({'cenario': nome, 'verificacao': 'passou', 'http_status': record['http_status']})
        print(nome, 'passou', flush=True)
    (directory/'resumo.json').write_text(json.dumps({'origem': 'execução real', 'cenarios': summary}, ensure_ascii=False, indent=2)+'\n')

if __name__ == '__main__':
    main()
