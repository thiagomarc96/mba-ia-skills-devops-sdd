import copy
import importlib.util
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("conferir", ROOT / "skill/scripts/conferir.py")
modulo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(modulo)


class ConferenciaTest(unittest.TestCase):
    def setUp(self):
        self.objetos = list(yaml.safe_load_all((ROOT / "manifests/nyx-api.yaml").read_text(encoding="utf-8")))
        self.deployment = next(x for x in self.objetos if x["kind"] == "Deployment")

    def regras(self):
        return {x["regra"] for x in modulo.conferir(self.objetos)}

    def test_recorte_mecanico_da_proposta(self):
        self.assertEqual([], modulo.conferir(self.objetos))

    def test_selector_incorreto(self):
        self.deployment["spec"]["template"]["metadata"]["labels"]["app.kubernetes.io/name"] = "outro"
        self.assertIn("1.4", self.regras())

    def test_latest_registry_e_segredo(self):
        c = self.deployment["spec"]["template"]["spec"]["containers"][0]
        c["image"] = "publico/app:latest"
        c["env"] = [{"name": "DB_PASSWORD", "value": "valor-de-teste"}]
        self.assertTrue({"3.1", "3.3", "3.7"}.issubset(self.regras()))
        self.assertNotIn("valor-de-teste", str(modulo.conferir(self.objetos)))

    def test_producao(self):
        self.deployment["spec"]["replicas"] = 1
        self.deployment["spec"].pop("strategy")
        self.assertTrue({"2.3", "2.4"}.issubset(self.regras()))

    def test_nome_namespace_labels(self):
        self.deployment["metadata"].update(name="NyxAPI", namespace="default", labels={})
        self.assertTrue({"1.1", "1.2", "1.3"}.issubset(self.regras()))

    def test_doc_invalido(self):
        with self.assertRaises(ValueError):
            modulo.conferir(["invalido"])


if __name__ == "__main__":
    unittest.main()
