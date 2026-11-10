"""Inventário SSH somente de leitura. Saídas e mensagens em português."""
import argparse
import ipaddress
import json
from pathlib import Path
import re
import subprocess
import sys

REGRAS = ('so.distribuicao', 'so.versao_minima', 'kernel.versao_minima',
          'servicos.ativos', 'servicos.proibidos', 'swap.habilitado',
          'portas_em_escuta.publicas_permitidas', 'portas_em_escuta.somente_rede_interna',
          'chaves_ssh.emitidas_por', 'ssh.login_de_root', 'ntp.sincronizado')


class ArgumentosSeguros(argparse.ArgumentParser):
    def error(self, message):
        # argparse normally echoes unknown argument values, including credentials.
        self.exit(3, 'Erro: argumentos inválidos ou ausentes. Consulte --help.\n')


def versao(valor):
    numeros = re.match(r'^(\d+(?:\.\d+)*)', str(valor))
    if not numeros:
        raise ValueError('versão inválida')
    return tuple(int(v) for v in numeros.group(1).split('.'))


def minimo(atual, esperado):
    a, b = versao(atual), versao(esperado)
    n = max(len(a), len(b))
    return a + (0,) * (n-len(a)) >= b + (0,) * (n-len(b))


def interno(bind):
    try:
        ip = ipaddress.ip_address(bind.split('%')[0])
        if getattr(ip, 'ipv4_mapped', None):
            ip = ip.ipv4_mapped
        redes = ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16', 'fc00::/7')
        return ip.is_loopback or any(ip in ipaddress.ip_network(r) for r in redes)
    except ValueError:
        return False


def avaliar(dados, baseline):
    inv, erros = dados['inventario'], dados.get('erros', {})
    severidades = {regra: nivel for nivel, regras in baseline['severidade'].items() for regra in regras}
    resultado = []
    for regra in REGRAS:
        grupo, campo = regra.split('.')
        esperado = baseline['esperado'][grupo][campo]
        encontrado = inv.get(grupo)
        item = {'regra': regra, 'esperado': esperado, 'encontrado': encontrado}
        try:
            if encontrado is None or grupo in erros:
                raise ValueError(erros.get(grupo, 'dado não coletado'))
            if regra in ('so.versao_minima', 'kernel.versao_minima'):
                encontrado = encontrado['versao']
                ok = minimo(encontrado, esperado)
            elif grupo == 'servicos':
                encontrado = sorted(x['nome'] for x in encontrado if x['estado'] == 'active')
                unidades = [v if '.' in v else v + '.service' for v in esperado]
                ok = all(x in encontrado for x in unidades) if campo == 'ativos' else not any(x in encontrado for x in unidades)
            elif grupo == 'portas_em_escuta':
                for p in encontrado:
                    if not isinstance(p['porta'], int) or not 0 <= p['porta'] <= 65535:
                        raise ValueError('porta inválida')
                publicas = [p for p in encontrado if not interno(p['bind'])]
                ok = (all(p['porta'] in esperado for p in publicas) if campo == 'publicas_permitidas'
                      else not any(p['porta'] in esperado for p in publicas))
            elif grupo == 'chaves_ssh':
                # Only a collector proving complete scope may omit this error.
                encontrado = [x['identificacao'] for x in encontrado]
                ok = all(x.rsplit('@', 1)[-1] == esperado for x in encontrado)
            else:
                encontrado = encontrado[campo]
                if encontrado is None:
                    raise ValueError('dado não coletado')
                if isinstance(esperado, bool) and not isinstance(encontrado, bool):
                    raise ValueError('tipo de dado inválido')
                ok = encontrado == esperado
            item.update(encontrado=encontrado, veredito='conforme' if ok else 'desvio')
            if not ok:
                item['severidade'] = severidades[regra]
        except (ValueError, KeyError, TypeError):
            item.update(veredito='nao_verificado', motivo=erros.get(grupo, 'dado ausente, incompleto ou inválido'))
        resultado.append(item)
    resumo = {k: sum(x['veredito'] == k for x in resultado) for k in ('conforme', 'desvio', 'nao_verificado')}
    resumo['por_severidade'] = {k: sum(x.get('severidade') == k for x in resultado) for k in baseline['severidade']}
    return {**dados, 'baseline': baseline['versao'], 'conformidade': resultado, 'resumo': resumo}


def codigo(relatorio):
    return 1 if relatorio['resumo']['desvio'] else 2 if relatorio['resumo']['nao_verificado'] else 0


def celula(valor):
    return json.dumps(valor, ensure_ascii=False).replace('|', '\\|').replace('\n', ' ')


def markdown(r):
    h = r['host']
    linhas = [f"# Inventário — {celula(h['hostname'])} ({celula(h['endereco'])})", f"Coletado em {h['coletado_em']} · baseline v{r['baseline']}", '', '## Desvios', '', '| Severidade | Regra | Esperado | Encontrado |', '|---|---|---|---|']
    for i in r['conformidade']:
        if i['veredito'] == 'desvio':
            linhas.append(f"| {i['severidade']} | {i['regra']} | {celula(i['esperado'])} | {celula(i['encontrado'])} |")
    linhas += ['', '## Não verificado', '', '| Regra | Motivo |', '|---|---|']
    for i in r['conformidade']:
        if i['veredito'] == 'nao_verificado':
            linhas.append(f"| {i['regra']} | {celula(i['motivo'])} |")
    linhas += ['', '## Conforme', '', ' · '.join(i['regra'] for i in r['conformidade'] if i['veredito'] == 'conforme'), '', '## Inventário', '', '```json', json.dumps(r['inventario'], ensure_ascii=False, indent=2), '```', '']
    return '\n'.join(linhas)


def erro_ssh(stderr):
    texto = stderr.lower()
    if 'permission denied' in texto:
        return 'autenticação SSH recusada'
    if 'host key verification failed' in texto or 'remote host identification has changed' in texto:
        return 'chave do host ausente ou divergente; verifique no OpenSSH'
    if 'connection refused' in texto:
        return 'serviço SSH recusou a conexão'
    if 'could not resolve' in texto:
        return 'nome do host não resolvido'
    return 'SSH indisponível ou coletor remoto não executado'


def coletar(host, usuario, chave, timeout=90):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:%-]*', host) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.-]*', usuario):
        raise ValueError('host ou usuário inválido')
    if not Path(chave).is_file():
        raise ValueError('arquivo da chave privada não encontrado')
    args = ['ssh', '-T', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', '-o', 'ConnectTimeout=10', '-o', 'IdentitiesOnly=yes', '-i', str(Path(chave).resolve()), '-l', usuario, '--', host, 'python3 -']
    try:
        p = subprocess.run(args, input=Path(__file__).with_name('coletor.py').read_text(encoding='utf-8'), capture_output=True, text=True, timeout=timeout, encoding='utf-8')
    except subprocess.TimeoutExpired:
        raise ValueError('tempo limite da coleta SSH excedido') from None
    except OSError:
        raise ValueError('OpenSSH não disponível na estação') from None
    if p.returncode:
        raise ValueError(erro_ssh(p.stderr))
    try:
        dados = json.loads(p.stdout)
        dados['host']['endereco'] = host
        if not isinstance(dados['inventario'], dict):
            raise ValueError()
        return dados
    except (ValueError, KeyError, TypeError):
        raise ValueError('resposta do coletor remoto inválida') from None


def main():
    parser = ArgumentosSeguros(description='Inventário Linux por SSH, somente leitura.', add_help=False)
    parser.add_argument('-h', '--help', action='help', help='mostrar esta ajuda e sair')
    parser._optionals.title = 'opções'
    parser.add_argument('--host', required=True)
    parser.add_argument('--usuario', required=True)
    parser.add_argument('--chave', required=True, help='caminho local; nunca conteúdo da chave')
    parser.add_argument('--baseline', default=str(Path(__file__).with_name('baseline.yaml')))
    parser.add_argument('--saida', default='saida')
    args = parser.parse_args()
    try:
        import yaml
        baseline = yaml.safe_load(Path(args.baseline).read_text(encoding='utf-8'))
        if set(REGRAS) != {r for regras in baseline['severidade'].values() for r in regras}:
            raise ValueError('baseline com regras de severidade ausentes ou inesperadas')
        # Validate every required expected value before opening SSH.
        for r in REGRAS:
            g, c = r.split('.')
            baseline['esperado'][g][c]
        r = avaliar(coletar(args.host, args.usuario, args.chave), baseline)
        destino = Path(args.saida)
        destino.mkdir(parents=True, exist_ok=True)
        (destino/'inventario.json').write_text(json.dumps(r, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        (destino/'inventario.md').write_text(markdown(r), encoding='utf-8')
        print('Relatórios JSON e Markdown gravados no diretório de saída.')
        return codigo(r)
    except ValueError as exc:
        # Only locally generated ValueError messages are surfaced by collection.
        print('Erro: ' + str(exc) if str(exc).startswith(('host ', 'arquivo ', 'tempo ', 'OpenSSH ', 'autenticação ', 'chave do host ', 'serviço SSH ', 'nome do host ', 'SSH ', 'resposta ', 'baseline ')) else 'Erro: entrada ou dados inválidos.', file=sys.stderr)
    except ImportError:
        print('Erro: instale a dependência PyYAML conforme o README.', file=sys.stderr)
    except Exception:
        print('Erro: não foi possível ler a configuração ou gravar os relatórios.', file=sys.stderr)
    return 3


if __name__ == '__main__':
    sys.exit(main())
