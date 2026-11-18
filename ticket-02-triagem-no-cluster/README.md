# Triagem real no cluster — T02

A [skill triagem-cluster](skill/SKILL.md) foi executada sobre três chamados do `kind-desafio03`, em 18/11/2026, usando [mcp-server-kubernetes 2.5.0](https://github.com/Flux159/mcp-server-kubernetes). A preparação dos incidentes foi externa à triagem. Nenhuma correção foi aplicada pela skill.

A configuração versionada está em [mcp/config.json](mcp/config.json), com [launcher](mcp/iniciar.sh), [wrapper kubectl](mcp/bin/kubectl) e [RBAC](mcp/rbac.yaml). O kubeconfig de `platform-ro` vem da variável `KUBECONFIG_RO`, herdada pelo processo, e fica fora do repo. O JSON usa caminhos relativos à raiz; clientes podem adaptar o caminho do launcher. Nenhuma interpolação `${...}` pelo cliente é necessária.

```sh
export KUBECONFIG_RO=/caminho/privado/ro.config
bash ticket-02-triagem-no-cluster/mcp/iniciar.sh
# Em outro processo, a partir da raiz:
python3 ticket-02-triagem-no-cluster/mcp/coletar.py
```

O cliente inicializa JSON-RPC por stdio, descobre as ferramentas e chama `kubectl_get` para deployments, pods, services, EndpointSlices e eventos, no namespace relevante. Usa YAML porque o servidor resume listagens JSON e omite detalhes importantes de spec/status. Requests, respostas e duração de cada chamada estão em [evidencias/t02](../evidencias/t02/).

| Chamado | Diagnóstico sustentado nas leituras |
|---|---|
| nyx-prod | Nova revisão com limite 24Mi termina OOMKilled/137 e entra em CrashLoopBackOff. Dois pods antigos de 256Mi e PostgreSQL continuam prontos. |
| orion-stg | Pull da tag v1.14.2 retorna NotFound, ErrImagePull/ImagePullBackOff. Rollout fica incompleto, com 2/3 réplicas prontas antigas; não há prova de indisponibilidade total. |
| nyx-stg | Service seleciona app=nyx-api, pod Ready usa app=nyxapi, EndpointSlice sem destinos. Proxy da API retorna ServiceUnavailable/503. |

Os [relatórios dos chamados](exemplos/chamados.json) cruzam pelo menos duas fontes por causa e distinguem banco saudável, revisão antiga e recurso defeituoso. A tag do chamado foi introduzida diretamente no lab; não há atribuição de conteúdo ao vídeo Loom privado.

A proteção combina `ALLOW_ONLY_NON_DESTRUCTIVE_TOOLS=true`, `ALLOW_ONLY_READONLY_TOOLS=true`, allowlist de cinco ferramentas, wrapper com contexto e verbos fixos e RBAC `view` por namespace. Uma ClusterRole adicional permite listar namespaces; em acesso-parcial, uma Role omite EndpointSlices. Secrets e exec não foram concedidos. O modo não destrutivo isolado ainda permitiria mutações; por isso as demais camadas são necessárias. Nesta versão do servidor, filtrar tools/list não impede chamar uma ferramenta oculta diretamente: a tentativa real de `kubectl_create` foi barrada pelo wrapper. O teste direto contra a API com a SA também recebeu Forbidden/403 e confirmou a ausência do ConfigMap. Evidências: `mcp-escrita-negada.json`, `rbac-escrita-negada.txt`, `rbac-secrets-negado.txt` e `ausencia-escrita.txt`.

Parte B: 10/10 rotas corretas. Parte C: saídas com/sem skill, tokens de entrada/saída/cache e tempo medidos em sessões independentes de Codex; [tabela, método e curadoria](../evidencias/t02/avaliacao.md). O experimento não demonstrou economia de tokens. Custo monetário fica null porque não foi fornecido. `python3 avaliar_codex.py` reproduz a avaliação a partir das coletas MCP congeladas e requer Codex autenticado. Os registros incluem saída integral, eventos do provedor e uso; os hashes das skills usados constam em `versoes-prompts.json`.
