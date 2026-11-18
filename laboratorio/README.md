# Laboratório local reproduzível

Este diretório prepara exclusivamente o cluster criado para o estudo, separado das skills de escrita e triagem. Requer Docker sem sudo, Python com PyYAML, npm/node e as versões kind 0.31.0, kubectl 1.35.0 e Trivy 0.69.3. [Instalação com checksums](../evidencias/preparo/instalar.sh) e logs do preparo ficam em `evidencias/preparo`. O primeiro download usou o sufixo incorreto `.sha256` do kind e recebeu 404; a repetição usou `.sha256sum` e validou os três checksums. Os dois primeiros pulls com timeout curto foram repetidos até concluir, com logs preservados.

Execute a partir da raiz em um laboratório novo; os scripts de criação de SA/Secret pressupõem recursos ainda ausentes. `LAB_RUNTIME` deve ficar fora do repo, com modo 700. Ele contém kubeconfigs privados em modo 600; nenhum arquivo dessa pasta deve ser versionado.

```sh
export PATH="$HOME/.local/bin:$PATH"
export LAB_RUNTIME="$(mktemp -d)"
export DIRETORIO_DOWNLOAD="$LAB_RUNTIME/downloads"
mkdir -p "$DIRETORIO_DOWNLOAD"
bash evidencias/preparo/instalar.sh
export KUBECONFIG="$LAB_RUNTIME/admin.config"
kind create cluster --name desafio03 --image kindest/node:v1.35.0
trivy config ticket-01-padrao-de-manifests/manifests/
python3 ticket-01-padrao-de-manifests/gerar_laboratorio.py
python3 laboratorio/preparar.py
# Aguarde apps e bancos prontos em todos os namespaces antes de provocar falhas.
for ns in nyx-dev orion-dev nyx-prod orion-stg nyx-stg; do
  kubectl --context kind-desafio03 -n "$ns" rollout status deployment --timeout=180s
done
python3 laboratorio/rbac.py
python3 laboratorio/incidentes.py
kubectl --context kind-desafio03 -n nyx-stg rollout status deployment/nyx-api --timeout=180s
kubectl --context kind-desafio03 -n acesso-parcial rollout status deployment --timeout=180s
export KUBECONFIG_RO="$LAB_RUNTIME/ro.config"
export KUBECONFIG_REVOGADO="$LAB_RUNTIME/revoked.config"
export KUBECONFIG_INDISPONIVEL="$LAB_RUNTIME/unavailable.config"
# Espere até o pod novo registrar OOMKilled e o pull da tag retornar erro.
python3 ticket-02-triagem-no-cluster/mcp/coletar.py
python3 laboratorio/falhas.py
python3 ticket-04-dashboard-do-cluster/coletar.py
python3 ticket-02-triagem-no-cluster/avaliar_codex.py
bash validar.sh
kind delete cluster --name desafio03
kind get clusters
docker ps --filter name=desafio03 --format '{{.Names}}'
```

Todas as chamadas kubectl do preparo usam `--context kind-desafio03`. O launcher MCP herda apenas o caminho da SA, elimina variáveis alternativas de kubeconfig e fixa contexto/timeout no wrapper. `config.json` não carrega credencial. `npx` verifica a integridade do pacote fixado (integridade registrada em `npm-pack.txt`). O teste direto de escrita 403 fica separado do wrapper para comprovar que o RBAC protege mesmo sem ele.

A imagem dos apps vem do Docker Hub público por digest. PostgreSQL 16.6-alpine usa emptyDir e não representa banco durável/HA. Reiniciar o pod do banco perde o conteúdo de estudo; após a alteração do securityContext isso exigiu reiniciar os apps para recriar o schema. O fechamento remove todos os dados efêmeros do cluster, conforme o escopo do exercício. Nenhum cluster externo é necessário.
