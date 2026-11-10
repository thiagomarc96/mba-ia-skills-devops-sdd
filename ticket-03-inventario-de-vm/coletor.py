"""Executado via stdin do Python remoto. Apenas consultas; nenhuma escrita."""
import datetime
import json
import os
import pathlib
import pwd
import re
import shlex
import socket
import subprocess

erros = {}


def comando(args):
    p = subprocess.run(args, capture_output=True, text=True, timeout=12)
    if p.returncode:
        raise RuntimeError("consulta indisponível ou sem permissão")
    return p.stdout.strip()


def coletar(nome, func):
    try:
        return func()
    except Exception:
        erros[nome] = "consulta indisponível ou exige privilégio não concedido"
        return None


def so():
    dados = {}
    for linha in pathlib.Path('/etc/os-release').read_text().splitlines():
        if '=' in linha:
            k, v = linha.split('=', 1)
            dados[k] = shlex.split(v)[0] if v else ''
    return {'distribuicao': dados['ID'], 'versao': dados['VERSION_ID']}


def servicos():
    saida = comando(['systemctl', 'list-units', '--type=service,socket', '--state=active', '--no-legend', '--plain', '--no-pager'])
    resultado = []
    for linha in saida.splitlines():
        partes = linha.split()
        if len(partes) < 4 or '.' not in partes[0]:
            raise ValueError('formato inesperado')
        resultado.append({'nome': partes[0], 'tipo': partes[0].rsplit('.', 1)[1], 'estado': partes[2]})
    return sorted(resultado, key=lambda x: x['nome'])


def swap():
    linhas = pathlib.Path('/proc/swaps').read_text().splitlines()[1:]
    tamanho = sum(int(l.split()[2]) * 1024 for l in linhas)
    return {'habilitado': bool(linhas), 'tamanho': tamanho, 'unidade': 'bytes'}


def portas():
    saida = comando(['ss', '-H', '-lntup'])
    resultado = []
    for linha in saida.splitlines():
        partes = linha.split(None, 6)
        if len(partes) < 6:
            raise ValueError('formato inesperado')
        bind, porta = partes[4].rsplit(':', 1)
        processo = re.search(r'users:\(\("([^"\n]+)"', partes[6] if len(partes) > 6 else '')
        resultado.append({'porta': int(porta), 'bind': bind.strip('[]'), 'processo': processo.group(1) if processo else None, 'protocolo': partes[0]})
    return sorted(resultado, key=lambda x: (x['porta'], x['bind'], x['protocolo']))


def configuracao_ssh(usuario):
    cliente, _, servidor, porta = os.environ['SSH_CONNECTION'].split()
    texto = comando(['/usr/sbin/sshd', '-T', '-C', f'user={usuario},addr={cliente},laddr={servidor},lport={porta},host={cliente}'])
    return dict(l.split(None, 1) for l in texto.splitlines() if ' ' in l)


def ssh_efetivo():
    valores = configuracao_ssh('root')
    valor = valores['permitrootlogin']
    if valor not in ('no', 'yes', 'prohibit-password', 'without-password', 'forced-commands-only'):
        raise ValueError('política desconhecida')
    return {'login_de_root': valor != 'no', 'politica': valor, 'escopo': 'conexao_atual'}


def chaves():
    # Scope: every NSS-enumerated account, for the current connection conditions.
    # Never execute AuthorizedKeysCommand or elevate privilege.
    resultado = []
    parcial = False
    for conta in pwd.getpwall():
        try:
            conf = configuracao_ssh(conta.pw_name)
            if conf.get('pubkeyauthentication') == 'no':
                continue
            if conf.get('authorizedkeyscommand', 'none') != 'none' or conf.get('trustedusercakeys', 'none') != 'none':
                parcial = True
            nomes = shlex.split(conf['authorizedkeysfile'])
        except Exception:
            parcial = True
            nomes = ['.ssh/authorized_keys', '.ssh/authorized_keys2']
        for nome in dict.fromkeys(nomes):
            if nome == 'none':
                continue
            tokens = {'h': conta.pw_dir, 'u': conta.pw_name, 'U': str(conta.pw_uid), '%': '%'}
            try:
                nome = re.sub(r'%(.)?', lambda m: tokens[m.group(1)], nome)
            except KeyError:
                parcial = True
                continue
            arquivo = pathlib.Path(nome)
            if not arquivo.is_absolute():
                arquivo = pathlib.Path(conta.pw_dir) / arquivo
            try:
                linhas = arquivo.read_text().splitlines()
            except FileNotFoundError:
                continue
            except (OSError, UnicodeError):
                parcial = True
                continue
            for linha in linhas:
                if not linha.strip() or linha.lstrip().startswith('#'):
                    continue
                try:
                    itens = shlex.split(linha)
                except ValueError:
                    parcial = True
                    continue
                indice = next((i for i, v in enumerate(itens) if v.startswith(('ssh-', 'ecdsa-', 'sk-'))), None)
                if indice is None or len(itens) <= indice + 1:
                    parcial = True
                    continue
                resultado.append({'usuario': conta.pw_name, 'identificacao': ' '.join(itens[indice + 2:])})
    if parcial:
        erros['chaves_ssh'] = 'cobertura parcial: configuração, arquivos ou fonte externa indisponíveis'
    return resultado


def ntp():
    ativo = comando(['timedatectl', 'show', '--property=NTPSynchronized', '--value'])
    if ativo not in ('yes', 'no'):
        raise ValueError('estado desconhecido')
    mecanismos = []
    for nome in ('chrony', 'chronyd', 'systemd-timesyncd', 'ntp', 'ntpd'):
        try:
            if comando(['systemctl', 'is-active', nome]) == 'active':
                mecanismos.append(nome)
        except Exception:
            pass
    return {'sincronizado': ativo == 'yes', 'mecanismo': ', '.join(mecanismos) or 'não identificado'}


def executar():
    inventario = {
    'so': coletar('so', so),
    'kernel': {'versao': os.uname().release},
    'servicos': coletar('servicos', servicos),
    'swap': coletar('swap', swap),
    'portas_em_escuta': coletar('portas_em_escuta', portas),
    'chaves_ssh': coletar('chaves_ssh', chaves),
    'ssh': coletar('ssh', ssh_efetivo),
    'ntp': coletar('ntp', ntp),
    }
    chaves_lidas = inventario['chaves_ssh']
    inventario['quantidade_chaves_ssh'] = len(chaves_lidas) if chaves_lidas is not None else None
    inventario['cobertura_chaves_ssh'] = 'parcial' if 'chaves_ssh' in erros else 'completa_para_contas_enumeradas_e_conexao_atual'
    print(json.dumps({'host': {'hostname': socket.gethostname(), 'coletado_em': datetime.datetime.now(datetime.timezone.utc).isoformat()}, 'inventario': inventario, 'erros': erros}, ensure_ascii=False))


if __name__ == '__main__':
    executar()
