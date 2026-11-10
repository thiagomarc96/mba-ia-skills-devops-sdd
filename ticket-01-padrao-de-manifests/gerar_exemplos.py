"""Executa o verificador local nos dois conjuntos de manifests."""
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
for nome, arquivo in [('conferencia', 'exemplos/manifesto-barrado.yaml'), ('escrita', 'manifests/nyx-api.yaml')]:
    result = subprocess.run([sys.executable, str(root/'skill/scripts/conferir.py'), str(root/arquivo)], text=True, encoding='utf-8', capture_output=True)
    if result.returncode not in (0, 1):
        raise SystemExit('Falha ao verificar ' + arquivo)
    dado = {'arquivo': arquivo, 'codigo': result.returncode, 'resultado': json.loads(result.stdout)}
    (root/'exemplos'/f'{nome}.json').write_text(json.dumps(dado, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
