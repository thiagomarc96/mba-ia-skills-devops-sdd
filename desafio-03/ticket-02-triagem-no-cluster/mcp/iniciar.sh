#!/usr/bin/env bash
set -euo pipefail
: "${KUBECONFIG_RO:?Defina o caminho do kubeconfig da ServiceAccount platform-ro}"
unset KUBECONFIG_YAML KUBECONFIG_JSON KUBECONFIG_PATH K8S_SERVER K8S_TOKEN
export K8S_CONTEXT=kind-desafio03
export KUBECONFIG="$KUBECONFIG_RO"
export ALLOW_ONLY_NON_DESTRUCTIVE_TOOLS=true
export ALLOW_ONLY_READONLY_TOOLS=true
export ALLOWED_TOOLS=kubectl_get,kubectl_describe,kubectl_logs,explain_resource,list_api_resources
# v2.5.0 não anexa --context: o wrapper fixa o alvo de cada processo kubectl.
export PATH="$(cd "$(dirname "$0")" && pwd)/bin:$HOME/.local/bin:$PATH"
exec npx --yes mcp-server-kubernetes@2.5.0
