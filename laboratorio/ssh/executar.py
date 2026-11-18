"""Executa duas coletas SSH reais e comprova a recusa após parar o servidor."""
import datetime
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import time

RAIZ = Path(__file__).resolve().parents[2]
COLETOR = RAIZ / 'desafio-03/ticket-03-inventario-de-vm/inventario.py'
SAIDA = RAIZ / 'evidencias/t03'
NOME = 'pessoal-desafio03-ssh'


def comando(args):
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout.strip()


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    # O Dockerfile não contém chave: os pares nascem fora do Git e são descartados.
    comando(['docker', 'build', '-t', NOME, str(Path(__file__).parent)])
    registros = []
    criado = False
    with tempfile.TemporaryDirectory(prefix='desafio03-ssh-') as pasta:
        privado = Path(pasta)
        chave = privado / 'identidade'
        hosts = privado / 'known_hosts'
        comando(['ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-C', 'estudo@metacortex-platform', '-f', str(chave)])
        try:
            identificador = comando(['docker', 'run', '-d', '--name', NOME, '--hostname', 'inventario-ssh-local', '-p', '127.0.0.1::22', '--mount', f'type=bind,src={chave}.pub,dst=/tmp/chave-publica,readonly', NOME])
            criado = True
            comando(['docker', 'exec', NOME, 'install', '-o', 'root', '-g', 'root', '-m', '600', '/tmp/chave-publica', '/root/.ssh/authorized_keys'])
            porta = int(comando(['docker', 'port', NOME, '22/tcp']).rsplit(':', 1)[1])
            for _ in range(50):
                try:
                    with socket.create_connection(('127.0.0.1', porta), timeout=1) as conexao:
                        if conexao.recv(200).startswith(b'SSH-'):
                            break
                except OSError:
                    pass
                time.sleep(0.1)
            else:
                raise RuntimeError('O servidor SSH não iniciou')
            # A chave pública é lida pelo canal Docker local confiável, sem aceitar TOFU pela rede.
            publica = comando(['docker', 'exec', NOME, 'cat', '/etc/ssh/ssh_host_ed25519_key.pub'])
            hosts.write_text(f'[127.0.0.1]:{porta} {publica}\n')
            argumentos = ['python3', str(COLETOR), '--host', '127.0.0.1', '--porta', str(porta), '--usuario', 'root', '--chave', str(chave), '--known-hosts', str(hosts)]
            relatorios = []
            for caso in ('primeira', 'segunda'):
                destino = SAIDA / caso
                inicio = datetime.datetime.now(datetime.timezone.utc).isoformat()
                processo = subprocess.run(argumentos + ['--saida', str(destino)], capture_output=True, text=True)
                (SAIDA / f'{caso}.codigo.txt').write_text(f'{processo.returncode}\n')
                (SAIDA / f'{caso}.stdout.txt').write_text(processo.stdout)
                (SAIDA / f'{caso}.stderr.txt').write_text(processo.stderr)
                if processo.returncode not in (0, 1, 2):
                    raise RuntimeError('Coleta SSH real falhou: ' + processo.stderr)
                relatorios.append(json.loads((destino / 'inventario.json').read_text()))
                registros.append({'caso': caso, 'iniciado_em': inicio, 'codigo_saida': processo.returncode})
            if relatorios[0]['host']['coletado_em'] == relatorios[1]['host']['coletado_em']:
                raise RuntimeError('Instantes das duas coletas coincidiram')
            iguais = relatorios[0]['conformidade'] == relatorios[1]['conformidade']
            comando(['docker', 'stop', NOME])
            with socket.socket() as conexao:
                conexao.settimeout(2)
                erro_tcp = conexao.connect_ex(('127.0.0.1', porta))
            if erro_tcp == 0:
                raise RuntimeError('A porta continuou acessível após parar o servidor')
            inicio = datetime.datetime.now(datetime.timezone.utc).isoformat()
            falha = subprocess.run(argumentos + ['--saida', str(SAIDA / 'inacessivel')], capture_output=True, text=True)
            if falha.returncode != 3 or 'recusou a conexão' not in falha.stderr:
                raise RuntimeError('O cenário inacessível não produziu a falha esperada')
            evidencia = {'origem': 'SSH real contra servidor parado', 'host': '127.0.0.1', 'porta': porta, 'iniciado_em': inicio, 'codigo_saida': falha.returncode, 'erro_tcp': erro_tcp, 'stderr': falha.stderr.strip(), 'relatorio_conformidade': None}
            (SAIDA / 'host-inacessivel.json').write_text(json.dumps(evidencia, ensure_ascii=False, indent=2) + '\n')
            (SAIDA / 'host-inacessivel.md').write_text(f'# Host inacessível\n\nServidor SSH parado após duas coletas reais. TCP em 127.0.0.1:{porta} recusado, erro {erro_tcp}.\n\n{falha.stderr.strip()}\n\nRetorno: {falha.returncode}. A CLI não emitiu relatório de conformidade; este arquivo registra a falha observada.\n')
            (SAIDA / 'host-inacessivel.codigo.txt').write_text(f'{falha.returncode}\n')
            (SAIDA / 'host-inacessivel.stderr.txt').write_text(falha.stderr)
            registros.append({'caso': 'host-inacessivel', 'iniciado_em': inicio, 'codigo_saida': falha.returncode})
            (SAIDA / 'execucao.json').write_text(json.dumps({'origem': 'OpenSSH real em container Docker local', 'container': identificador, 'imagem': comando(['docker', 'inspect', '--format', '{{.Image}}', NOME]), 'porta_local': porta, 'autenticacao': 'chave efêmera fora do Git', 'validacao_host': 'chave pública lida via Docker e conhecida explicitamente', 'execucoes': registros, 'conformidade_igual_nas_duas_coletas': iguais}, ensure_ascii=False, indent=2) + '\n')
            if not iguais:
                raise RuntimeError('Os vereditos mudaram entre as duas coletas; examine os relatórios')
        finally:
            if criado:
                comando(['docker', 'rm', '-f', NOME])
                restante = comando(['docker', 'ps', '-a', '--filter', f'name=^/{NOME}$', '--format', '{{.Names}}'])
                if restante:
                    raise RuntimeError('O container ainda está presente')
                (SAIDA / 'limpeza.txt').write_text('Container de SSH removido; docker ps -a com nome exato retornou vazio.\nChave privada e known_hosts temporários descartados fora do Git.\n')
    print('Duas coletas SSH reais e recusa TCP verificadas. Container removido.')


if __name__ == '__main__':
    main()
