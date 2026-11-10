import copy
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch
import inventario as app


def baseline():
    return {'versao': 1, 'esperado': {
        'so': {'distribuicao': 'ubuntu', 'versao_minima': '22.04'},
        'kernel': {'versao_minima': '6.5'},
        'servicos': {'ativos': ['ssh', 'containerd', 'node_exporter', 'chrony'], 'proibidos': ['telnet.socket', 'rpcbind.socket']},
        'swap': {'habilitado': False},
        'portas_em_escuta': {'publicas_permitidas': [22], 'somente_rede_interna': [9100]},
        'chaves_ssh': {'emitidas_por': 'metacortex-platform'},
        'ssh': {'login_de_root': False}, 'ntp': {'sincronizado': True}},
        'severidade': {'critico': list(app.REGRAS[5:9]), 'alto': list(app.REGRAS[:2]) + list(app.REGRAS[3:5]) + ['ssh.login_de_root'], 'medio': ['kernel.versao_minima', 'ntp.sincronizado']}}


def dados():
    return {'host': {'endereco': '192.0.2.10', 'hostname': 'teste', 'coletado_em': '2026-11-10T00:00:00Z'}, 'inventario': {
        'so': {'distribuicao': 'ubuntu', 'versao': '24.04'}, 'kernel': {'versao': '6.8.0-generic'},
        'servicos': [{'nome': x+'.service', 'tipo': 'service', 'estado': 'active'} for x in ['ssh', 'containerd', 'node_exporter', 'chrony']],
        'swap': {'habilitado': False, 'tamanho': 0},
        'portas_em_escuta': [{'porta': 22, 'bind': '0.0.0.0', 'processo': 'sshd'}, {'porta': 9100, 'bind': '10.0.0.10', 'processo': 'node_exporter'}],
        'chaves_ssh': [{'identificacao': 'operador@metacortex-platform'}],
        'ssh': {'login_de_root': False}, 'ntp': {'sincronizado': True, 'mecanismo': 'chrony'}}}


class TestInventario(unittest.TestCase):
    def test_argumentos_nao_expoem_valores(self):
        segredo = 'VALOR-QUE-NAO-DEVE-APARECER'
        erro = io.StringIO()
        with patch.object(sys, 'argv', ['inventario.py', '--host', '192.0.2.10', '--usuario', 'user', '--chave', 'arquivo', segredo]), contextlib.redirect_stderr(erro):
            with self.assertRaises(SystemExit) as exc:
                app.main()
        self.assertEqual(exc.exception.code, 3)
        self.assertNotIn(segredo, erro.getvalue())

    def test_conforme(self):
        r = app.avaliar(dados(), baseline())
        self.assertEqual(r['resumo']['conforme'], 11)
        self.assertEqual(app.codigo(r), 0)

    def test_desvios_classificados(self):
        d = dados()
        d['inventario']['swap']['habilitado'] = True
        d['inventario']['kernel']['versao'] = '5.15.0-118-generic'
        d['inventario']['portas_em_escuta'][1]['bind'] = '::'
        r = app.avaliar(d, baseline())
        desvios = {x['regra']: x['severidade'] for x in r['conformidade'] if x['veredito'] == 'desvio'}
        self.assertEqual(desvios, {'kernel.versao_minima': 'medio', 'swap.habilitado': 'critico', 'portas_em_escuta.publicas_permitidas': 'critico', 'portas_em_escuta.somente_rede_interna': 'critico'})
        self.assertEqual(app.codigo(r), 1)

    def test_socket_proibido(self):
        d = dados()
        d['inventario']['servicos'].append({'nome': 'rpcbind.socket', 'tipo': 'socket', 'estado': 'active'})
        self.assertEqual(app.avaliar(d, baseline())['resumo']['desvio'], 1)

    def test_parcial_nao_e_conforme(self):
        d = dados()
        d['erros'] = {'chaves_ssh': 'escopo parcial'}
        d['inventario']['ssh'] = None
        r = app.avaliar(d, baseline())
        self.assertEqual(r['resumo']['nao_verificado'], 2)
        self.assertEqual(app.codigo(r), 2)

    def test_repeticao_e_formatos(self):
        d = dados()
        a = app.avaliar(copy.deepcopy(d), baseline())
        d['host']['coletado_em'] = '2026-11-10T00:01:00Z'
        b = app.avaliar(d, baseline())
        self.assertEqual(a['conformidade'], b['conformidade'])
        md = app.markdown(b)
        self.assertTrue(all(r in md for r in app.REGRAS))

    def test_redes(self):
        for v in ['10.0.0.1', '192.168.1.2', '172.16.1.2', '::1', 'fd00::1', '::ffff:10.0.0.1']:
            self.assertTrue(app.interno(v), v)
        for v in ['0.0.0.0', '::', '*', '8.8.8.8', '192.0.2.10']:
            self.assertFalse(app.interno(v), v)

    def test_versoes(self):
        self.assertTrue(app.minimo('6.10.0', '6.5'))
        self.assertTrue(app.minimo('22.04', '22.4.0'))
        self.assertFalse(app.minimo('5.15.0-118-generic', '6.5'))

    def test_erro_ssh_nao_reproduz_segredo(self):
        self.assertEqual(app.erro_ssh('Permission denied: segredo'), 'autenticação SSH recusada')
        self.assertNotIn('segredo', app.erro_ssh('segredo'))

    def test_host_invalido_sem_subprocesso(self):
        with patch('subprocess.run') as run:
            with self.assertRaises(ValueError):
                app.coletar('-oProxyCommand=segredo', 'user', 'chave')
            run.assert_not_called()

    def test_comando_somente_leitura(self):
        import subprocess
        with patch('pathlib.Path.is_file', return_value=True), patch('pathlib.Path.read_text', return_value='print(1)'), patch('subprocess.run', return_value=subprocess.CompletedProcess([], 255, '', 'Permission denied: segredo')) as run:
            with self.assertRaisesRegex(ValueError, '^autenticação SSH recusada$'):
                app.coletar('192.0.2.10', 'operador', 'chave')
            args = run.call_args.args[0]
            self.assertIn('StrictHostKeyChecking=yes', args)
            self.assertEqual(args[-1], 'python3 -')
            self.assertNotIn('shell', run.call_args.kwargs)


class TestChaves(unittest.TestCase):
    def setUp(self):
        conta = types.SimpleNamespace(pw_name='operador', pw_dir='/home/operador', pw_uid=1000)
        fake_pwd = types.SimpleNamespace(getpwall=lambda: [conta])
        spec = importlib.util.spec_from_file_location('coletor_teste', Path(__file__).with_name('coletor.py'))
        self.mod = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'pwd': fake_pwd}):
            spec.loader.exec_module(self.mod)
        self.conf = {'pubkeyauthentication': 'yes', 'authorizedkeysfile': '%h/.ssh/authorized_keys', 'authorizedkeyscommand': 'none', 'trustedusercakeys': 'none'}

    def test_cobertura_completa(self):
        with patch.object(self.mod, 'configuracao_ssh', return_value=self.conf), patch.object(self.mod.pathlib.Path, 'read_text', return_value='ssh-ed25519 BASE64 operador@metacortex-platform\n'):
            chaves = self.mod.chaves()
        self.assertEqual(chaves, [{'usuario': 'operador', 'identificacao': 'operador@metacortex-platform'}])
        self.assertNotIn('chaves_ssh', self.mod.erros)

    def test_arquivo_inacessivel(self):
        with patch.object(self.mod, 'configuracao_ssh', return_value=self.conf), patch.object(self.mod.pathlib.Path, 'read_text', side_effect=PermissionError('caminho privado')):
            self.assertEqual(self.mod.chaves(), [])
        self.assertIn('chaves_ssh', self.mod.erros)
        self.assertNotIn('caminho privado', self.mod.erros['chaves_ssh'])

    def test_arquivo_ausente_nao_e_falha(self):
        with patch.object(self.mod, 'configuracao_ssh', return_value=self.conf), patch.object(self.mod.pathlib.Path, 'read_text', side_effect=FileNotFoundError()):
            self.assertEqual(self.mod.chaves(), [])
        self.assertNotIn('chaves_ssh', self.mod.erros)

    def test_fonte_externa_nao_e_executada(self):
        self.conf['authorizedkeyscommand'] = '/usr/bin/fonte-externa'
        with patch.object(self.mod, 'configuracao_ssh', return_value=self.conf), patch.object(self.mod.pathlib.Path, 'read_text', side_effect=FileNotFoundError()), patch.object(self.mod, 'comando') as comando:
            self.mod.chaves()
        comando.assert_not_called()
        self.assertIn('chaves_ssh', self.mod.erros)

    def test_configuracao_indisponivel(self):
        with patch.object(self.mod, 'configuracao_ssh', side_effect=PermissionError()), patch.object(self.mod.pathlib.Path, 'read_text', side_effect=FileNotFoundError()):
            self.mod.chaves()
        self.assertIn('chaves_ssh', self.mod.erros)

    def test_contagem_explicita(self):
        stdout = io.StringIO()
        with patch.object(self.mod, 'coletar', side_effect=lambda nome, f: [{'identificacao': 'teste'}] if nome == 'chaves_ssh' else None), patch.object(self.mod.os, 'uname', return_value=types.SimpleNamespace(release='6.8'), create=True), contextlib.redirect_stdout(stdout):
            self.mod.executar()
        self.assertEqual(json.loads(stdout.getvalue())['inventario']['quantidade_chaves_ssh'], 1)


if __name__ == '__main__':
    unittest.main()
