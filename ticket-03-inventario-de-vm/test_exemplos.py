import copy
import json
from pathlib import Path
import tempfile
import unittest
import gerar_exemplos as sim


class TestExemplos(unittest.TestCase):
    def test_relatorios_e_repeticao(self):
        with tempfile.TemporaryDirectory() as pasta:
            r = sim.gerar(pasta)
            raiz = Path(pasta)
            self.assertEqual(r['conforme']['resumo']['conforme'], 11)
            self.assertEqual(r['parcial']['resumo']['nao_verificado'], 2)
            self.assertEqual(r['desvio']['resumo']['desvio'], 6)
            for nome, codigo in [('conforme', 0), ('desvio', 1), ('parcial', 2), ('repeticao', 1), ('host-inacessivel', 3)]:
                self.assertEqual((raiz / f'{nome}.codigo.txt').read_text().strip(), str(codigo))
                self.assertEqual(json.loads((raiz / f'{nome}.json').read_text(encoding='utf-8'))['origem'], 'fixture')
                self.assertTrue((raiz / f'{nome}.md').is_file())
            a, b = copy.deepcopy(r['desvio']), copy.deepcopy(r['repeticao'])
            self.assertNotEqual(a['host'].pop('coletado_em'), b['host'].pop('coletado_em'))
            self.assertEqual(a, b)

    def test_inacessivel_sem_conformidade(self):
        r = sim.falha_inacessivel()
        self.assertEqual(r['codigo_saida'], 3)
        self.assertIsNone(r['relatorio_conformidade'])
        self.assertEqual(r['erro'], 'Erro: serviço SSH recusou a conexão')
        self.assertNotIn('chave-fixture', r['erro'])


if __name__ == '__main__':
    unittest.main()
