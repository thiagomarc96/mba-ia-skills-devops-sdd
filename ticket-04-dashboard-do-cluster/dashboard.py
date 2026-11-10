"""Dashboard local: somente leituras kubectl; sem dependências Python externas."""
import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

RESOURCES = ('namespaces', 'pods', 'deployments', 'services',
             'endpointslices.discovery.k8s.io', 'events')


def error_message(stderr):
    value = stderr.lower()
    if 'forbidden' in value:
        return 'Permissão negada para este recurso.'
    if any(s in value for s in ('unauthorized', 'expired', 'credentials', 'must be logged')):
        return 'Autenticação recusada ou expirada. Confira o acesso fora do dashboard.'
    if any(s in value for s in ('refused', 'timeout', 'timed out', 'no such host', 'unable to connect')):
        return 'Cluster indisponível ou conexão sem resposta.'
    return 'Falha na consulta. Confira kubeconfig, acesso e kubectl fora do dashboard.'


class Kubernetes:
    def __init__(self, run=subprocess.run):
        self.run = run
        self.context = None
        self.start_error = None
        try:
            self.context = self._call(['config', 'current-context']).strip()
            if not self.context:
                self.start_error = 'Nenhum contexto corrente configurado. Corrija e reinicie.'
        except RuntimeError as exc:
            self.start_error = str(exc)

    def _call(self, args):
        try:
            result = self.run(['kubectl', *args], capture_output=True, text=True,
                              encoding='utf-8', errors='replace', timeout=15,
                              shell=False)
        except FileNotFoundError:
            raise RuntimeError('kubectl não encontrado no PATH. Instale e reinicie.') from None
        except subprocess.TimeoutExpired:
            raise RuntimeError('Cluster indisponível ou consulta excedeu 15 segundos.') from None
        except OSError:
            raise RuntimeError('Não foi possível executar kubectl.') from None
        if result.returncode:
            raise RuntimeError(error_message(result.stderr or ''))
        return result.stdout

    def get(self, resource, namespace=None):
        if resource not in RESOURCES:
            raise ValueError('Recurso não permitido.')
        if namespace is not None and not valid_namespace(namespace):
            raise ValueError('Namespace inválido.')
        if self.start_error:
            raise RuntimeError(self.start_error)
        args = ['--context', self.context, '--request-timeout=10s', 'get', resource]
        if namespace is not None:
            args.extend(['--namespace', namespace])
        args.extend(['--output=json'])
        try:
            data = json.loads(self._call(args))
            if not isinstance(data, dict) or not isinstance(data.get('items'), list):
                raise ValueError()
            if not all(isinstance(item, dict) for item in data['items']):
                raise ValueError()
            return data['items']
        except (ValueError, TypeError):
            raise RuntimeError('Resposta JSON inválida recebida do kubectl.') from None


def valid_namespace(value):
    return bool(re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', value))


def pod_row(pod):
    status = pod.get('status') or {}
    containers = (status.get('initContainerStatuses') or []) + (status.get('containerStatuses') or [])
    reasons = []
    for container in containers:
        for state_name in ('state', 'lastState'):
            state = container.get(state_name) or {}
            for kind in ('waiting', 'terminated'):
                reason = (state.get(kind) or {}).get('reason')
                if reason and reason not in reasons:
                    reasons.append(reason)
    ready = any(c.get('type') == 'Ready' and c.get('status') == 'True'
                for c in status.get('conditions') or [])
    return {'nome': (pod.get('metadata') or {}).get('name', ''),
            'fase': status.get('phase', 'Desconhecida'),
            'pronto': ready, 'reinicios': sum(c.get('restartCount') or 0 for c in containers),
            'motivo': ', '.join(reasons) or status.get('reason') or '—'}


def service_rows(services, slices):
    rows = []
    for service in services:
        name = (service.get('metadata') or {}).get('name', '')
        spec = service.get('spec') or {}
        if spec.get('type') == 'ExternalName':
            endpoint = 'DNS externo (sem EndpointSlice)'
        elif slices is None:
            endpoint = 'Desconhecido: leitura de EndpointSlice indisponível'
        else:
            ready, unknown = set(), set()
            for item in slices:
                labels = (item.get('metadata') or {}).get('labels') or {}
                if labels.get('kubernetes.io/service-name') != name:
                    continue
                for entry in item.get('endpoints') or []:
                    condition = (entry.get('conditions') or {}).get('ready')
                    addresses = entry.get('addresses') or []
                    if condition is True:
                        ready.update(addresses)
                    elif condition is None:
                        unknown.update(addresses)
            endpoint = f'{len(ready)} endereço(s) pronto(s)' if ready else 'Sem endpoint pronto'
            if unknown:
                endpoint += f'; {len(unknown)} com prontidão desconhecida'
        rows.append({'nome': name, 'tipo': spec.get('type', 'ClusterIP'), 'endpoints': endpoint})
    return rows


def snapshot(client, namespace):
    data, errors = {}, {}
    for resource in RESOURCES:
        try:
            data[resource] = client.get(resource, None if resource == 'namespaces' else namespace)
        except RuntimeError as exc:
            data[resource] = None
            errors[resource] = str(exc)
    def items(key):
        return data[key] or []
    deployments = [{'nome': (d.get('metadata') or {}).get('name', ''),
                    'prontos': (d.get('status') or {}).get('readyReplicas') or 0,
                    'desejados': (d.get('spec') or {}).get('replicas', 1)}
                   for d in items('deployments')]
    events = []
    for event in items('events'):
        meta = event.get('metadata') or {}
        events.append({'nome': (event.get('involvedObject') or {}).get('name', meta.get('name', '')),
                       'tipo': event.get('type', ''), 'motivo': event.get('reason', ''),
                       'mensagem': event.get('message', ''),
                       'quando': (event.get('series') or {}).get('lastObservedTime')
                                 or event.get('lastTimestamp') or event.get('eventTime')
                                 or meta.get('creationTimestamp') or ''})
    return {'contexto': client.context, 'namespace': namespace,
            'coletado_em': datetime.now(timezone.utc).isoformat(), 'erros': errors,
            'namespaces': sorted((n.get('metadata') or {}).get('name', '') for n in items('namespaces')),
            'pods': [pod_row(p) for p in items('pods')], 'deployments': deployments,
            'services': service_rows(items('services'), data['endpointslices.discovery.k8s.io']),
            'events': sorted(events, key=lambda e: e['quando'], reverse=True)[:50]}


def handler_for(client):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # Não registrar queries, dados ou erros brutos do cluster.

        def send(self, status, content, mime):
            self.send_response(status)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(content)

        def do_GET(self):
            if self.headers.get('Host') != f'127.0.0.1:{self.server.server_port}':
                self.send(403, b'Host nao permitido.', 'text/plain; charset=utf-8')
                return
            parsed = urlsplit(self.path)
            static = {'/': ('index.html', 'text/html'), '/app.js': ('app.js', 'text/javascript'),
                      '/style.css': ('style.css', 'text/css')}
            if parsed.path in static:
                filename, mime = static[parsed.path]
                self.send(200, (Path(__file__).parent / 'static' / filename).read_bytes(), mime + '; charset=utf-8')
                return
            if parsed.path != '/api/estado':
                self.send(404, b'Nao encontrado.', 'text/plain; charset=utf-8')
                return
            query = parse_qs(parsed.query)
            namespace = query.get('namespace', ['default'])[0]
            if not valid_namespace(namespace):
                self.send(400, b'Namespace invalido.', 'text/plain; charset=utf-8')
                return
            try:
                content = json.dumps(snapshot(client, namespace), ensure_ascii=False).encode('utf-8')
                self.send(200, content, 'application/json; charset=utf-8')
            except Exception:
                self.send(500, b'Falha interna ao processar a consulta.', 'text/plain; charset=utf-8')
    return Handler


def main():
    parser = argparse.ArgumentParser(description='Dashboard Kubernetes local, somente leitura.')
    parser.add_argument('--porta', type=int, default=8088)
    args = parser.parse_args()
    if not 1024 <= args.porta <= 65535:
        parser.error('porta deve estar entre 1024 e 65535')
    client = Kubernetes()
    try:
        server = HTTPServer(('127.0.0.1', args.porta), handler_for(client))
    except OSError:
        parser.exit(1, 'Não foi possível abrir a porta local. Escolha outra com --porta.\n')
    print(f'Acesse http://127.0.0.1:{args.porta}. Somente leitura. Ctrl+C para sair.')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
