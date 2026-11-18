#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m unittest discover -s desafio-03/ticket-01-padrao-de-manifests/tests -v
(cd desafio-03/ticket-03-inventario-de-vm && python3 -m unittest -v)
(cd desafio-03/ticket-04-dashboard-do-cluster && python3 -m unittest -v)
python3 -m compileall -q desafio-03/ticket-01-padrao-de-manifests desafio-03/ticket-02-triagem-no-cluster desafio-03/ticket-03-inventario-de-vm desafio-03/ticket-04-dashboard-do-cluster laboratorio
node --check desafio-03/ticket-04-dashboard-do-cluster/static/app.js
bash -n desafio-03/ticket-02-triagem-no-cluster/mcp/iniciar.sh desafio-03/ticket-02-triagem-no-cluster/mcp/bin/kubectl evidencias/preparo/instalar.sh validar.sh
python3 laboratorio/validar_artefatos.py
(cd evidencias && sha256sum -c SHA256SUMS)
git diff --check
