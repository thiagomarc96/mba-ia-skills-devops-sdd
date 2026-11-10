"""Cenários sintéticos: executam o backend HTTP sem kubectl ou cluster."""
import argparse
import json
from copy import deepcopy
from http.server import HTTPServer
from pathlib import Path
from threading import Thread
from urllib.request import urlopen

from dashboard import RESOURCES, handler_for

CASOS = {
    'nyx-dev': 'kube-news com aplicação e PostgreSQL prontos',
    'orion-dev': 'fake-shop com aplicação e PostgreSQL prontos',
    'nyx-prod': 'kube-news com CrashLoopBackOff e OOMKilled anterior',
    'orion-stg': 'fake-shop em ImagePullBackOff',
    'nyx-stg': 'kube-news pronto, Service sem endpoint',
    'acesso-parcial': 'leitura de EndpointSlice proibida; demais recursos disponíveis',
    'credencial-expirada': 'autenticação expirada em todas as consultas do namespace',
    'cluster-indisponivel': 'conexão indisponível em todas as consultas do namespace',
}


def ambiente(namespace):
    """Fixtures mínimas da API, não manifests e não evidências de workloads reais."""
    shop = namespace.startswith('orion')
    component = 'orion-web' if shop else 'nyx-api'
    product = 'fake-shop' if shop else 'kube-news'
    image = 'fabricioveronez/fake-shop:v1' if shop else 'fabricioveronez/kube-news:v1'
    app_port = 5000 if shop else 8080
    database = 'orion-postgres' if shop else 'nyx-postgres'
    data = {resource: [] for resource in RESOURCES}
    for i, (name, container_image, port) in enumerate(((component, image, app_port),
                                                     (database, 'postgres:16-alpine', 5432))):
        data['pods'].append({'metadata': {'name': name + '-simulado', 'namespace': namespace,
                                         'labels': {'app': name, 'produto': product}},
                             'spec': {'containers': [{'name': name, 'image': container_image,
                                                      'ports': [{'containerPort': port}]}]},
                             'status': {'phase': 'Running',
                                        'conditions': [{'type': 'Ready', 'status': 'True'}],
                                        'containerStatuses': [{'name': name, 'ready': True,
                                                               'restartCount': 0, 'state': {'running': {}}}]}})
        data['deployments'].append({'metadata': {'name': name, 'namespace': namespace},
                                    'spec': {'replicas': 1}, 'status': {'readyReplicas': 1}})
        data['services'].append({'metadata': {'name': name, 'namespace': namespace},
                                 'spec': {'type': 'ClusterIP', 'selector': {'app': name},
                                          'ports': [{'port': port, 'targetPort': port}]}})
        data['endpointslices.discovery.k8s.io'].append({
            'metadata': {'name': name + '-slice', 'namespace': namespace,
                         'labels': {'kubernetes.io/service-name': name}},
            'addressType': 'IPv4', 'endpoints': [{'addresses': [f'10.244.0.{i+10}'],
                                                'conditions': {'ready': True}}]})
    reason = None
    if namespace == 'nyx-prod':
        status = data['pods'][0]['status']
        status['conditions'][0]['status'] = 'False'
        status['containerStatuses'][0].update(ready=False, restartCount=17,
            state={'waiting': {'reason': 'CrashLoopBackOff'}},
            lastState={'terminated': {'reason': 'OOMKilled', 'exitCode': 137}})
        data['deployments'][0]['status'] = {}
        data['endpointslices.discovery.k8s.io'][0]['endpoints'][0]['conditions']['ready'] = False
        reason = 'BackOff'
    elif namespace == 'orion-stg':
        status = data['pods'][0]['status']
        status['phase'] = 'Pending'
        status['conditions'][0]['status'] = 'False'
        status['containerStatuses'][0].update(ready=False, state={'waiting': {'reason': 'ImagePullBackOff'}})
        data['pods'][0]['spec']['containers'][0]['image'] = 'fabricioveronez/fake-shop:v1.14.2'
        data['deployments'][0]['spec']['replicas'] = 3
        data['deployments'][0]['status'] = {}
        data['endpointslices.discovery.k8s.io'][0]['endpoints'] = []
        reason = 'Failed'
    elif namespace == 'nyx-stg':
        data['pods'][0]['metadata']['labels']['app'] = 'nyxapi'
        del data['endpointslices.discovery.k8s.io'][0]['endpoints']
        reason = 'SemEndpoint'
    data['events'] = [{'metadata': {'name': component + '.simulado', 'namespace': namespace},
                       'involvedObject': {'kind': 'Pod', 'name': component + '-simulado'},
                       'type': 'Warning' if reason else 'Normal',
                       'reason': reason or 'Started',
                       'message': 'Evento sintético: ' + CASOS.get(namespace, 'ambiente de demonstração'),
                       'lastTimestamp': '2026-11-10T12:00:00Z'}]
    return data


class ClusterSimulado:
    context = 'laboratorio-exemplo'
    simulado = True

    def __init__(self):
        self.consultas = []

    def get(self, resource, namespace=None):
        if resource not in RESOURCES:
            raise ValueError('Recurso não permitido.')
        self.consultas.append({'recurso': resource, 'namespace': namespace})
        if resource == 'namespaces':
            return [{'metadata': {'name': name}} for name in CASOS]
        if namespace == 'credencial-expirada':
            raise RuntimeError('Autenticação recusada ou expirada. Confira o acesso fora do dashboard.')
        if namespace == 'cluster-indisponivel':
            raise RuntimeError('Cluster indisponível ou conexão sem resposta.')
        if namespace == 'acesso-parcial' and resource == 'endpointslices.discovery.k8s.io':
            raise RuntimeError('Permissão negada para este recurso.')
        return deepcopy(ambiente(namespace)[resource])


def gerar_evidencias():
    """Testa o servidor real por HTTP em loopback; adapter de Kubernetes é falso."""
    client = ClusterSimulado()
    server = HTTPServer(('127.0.0.1', 0), handler_for(client))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f'http://127.0.0.1:{server.server_port}'
    directory = Path(__file__).parent / 'exemplos' / 'fixtures'
    directory.mkdir(parents=True, exist_ok=True)
    summary = {'tipo': 'exemplo', 'origem': 'cenários do dashboard',
               'comando': 'python simular.py --gerar-exemplos', 'cenarios': []}
    try:
        for namespace, description in CASOS.items():
            client.consultas.clear()
            with urlopen(base + '/api/estado?namespace=' + namespace, timeout=10) as response:
                status = response.status
                result = json.load(response)
            assert result['simulado'] is True
            assert status == 200
            if namespace == 'nyx-prod':
                assert 'OOMKilled' in result['pods'][0]['motivo']
                assert result['pods'][0]['reinicios'] == 17
            if namespace == 'orion-stg':
                assert result['deployments'][0]['prontos'] == 0
                assert 'ImagePullBackOff' in result['pods'][0]['motivo']
            if namespace == 'nyx-stg':
                assert result['services'][0]['endpoints'] == 'Sem endpoint pronto'
                assert result['pods'][0]['pronto'] is True
            if namespace == 'acesso-parcial':
                assert len(result['erros']) == 1 and len(result['pods']) == 2
                assert 'Desconhecido' in result['services'][0]['endpoints']
            if namespace in ('credencial-expirada', 'cluster-indisponivel'):
                assert len(result['erros']) == 5 and result['pods'] == []
            if namespace in ('nyx-dev', 'orion-dev'):
                assert not result['erros'] and len(result['pods']) == 2
            evidence = {'tipo': 'exemplo', 'cenario': description, 'http_status': status,
                        'entrada_sintetica': ambiente(namespace), 'consultas': list(client.consultas),
                        'resposta': result}
            (directory / f'{namespace}.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            summary['cenarios'].append({'namespace': namespace, 'verificacao': 'passou', 'http_status': status})
        for path in ('/', '/app.js', '/style.css'):
            with urlopen(base + path, timeout=10) as response:
                assert response.status == 200 and response.read()
        summary['arquivos_estaticos'] = '3 rotas HTTP verificadas'
        (directory / 'resumo.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('8 cenários passaram pelo backend HTTP; saídas em exemplos/fixtures/.')
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def main():
    parser = argparse.ArgumentParser(description='Demonstração sintética, sem conexão a cluster.')
    parser.add_argument('--gerar-exemplos', action='store_true')
    parser.add_argument('--porta', type=int, default=8089)
    args = parser.parse_args()
    if args.gerar_exemplos:
        gerar_evidencias()
        return
    if not 1024 <= args.porta <= 65535:
        parser.error('porta deve estar entre 1024 e 65535')
    server = HTTPServer(('127.0.0.1', args.porta), handler_for(ClusterSimulado()))
    print(f'EXEMPLO: http://127.0.0.1:{args.porta}. Escolha um namespace para ver o cenário.')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
