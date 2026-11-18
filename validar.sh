#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m unittest discover -s ticket-01-padrao-de-manifests/tests -v
(cd ticket-03-inventario-de-vm && python3 -m unittest -v)
(cd ticket-03-inventario-de-vm && python3 gerar_exemplos.py)
(cd ticket-04-dashboard-do-cluster && python3 -m unittest -v)
python3 -m compileall -q ticket-01-padrao-de-manifests ticket-02-triagem-no-cluster ticket-03-inventario-de-vm ticket-04-dashboard-do-cluster laboratorio
node --check ticket-04-dashboard-do-cluster/static/app.js
bash -n ticket-02-triagem-no-cluster/mcp/iniciar.sh ticket-02-triagem-no-cluster/mcp/bin/kubectl evidencias/preparo/instalar.sh validar.sh
git diff --check
