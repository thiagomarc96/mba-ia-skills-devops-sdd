# Avaliação medida — Partes B e C

17 processos `codex exec --ignore-user-config --skip-git-repo-check --ephemeral --sandbox read-only --json -`, sem alteração de modelo entre casos; modelo padrão do executável Codex. Cada processo recebeu somente o prompt e foi instruído a não usar ferramentas. Parte A usa as chamadas reais do MCP; Parte C compara interpretação sobre as mesmas saídas congeladas dessas chamadas (não refaz a coleta por modelo). Até 3 execuções concorrentes; cache e contenção variam. Uma amostra por célula, sem inferência estatística ou promessa de economia. Custo monetário não fornecido pelo provedor: null.

Partes A/C não confundem Ready com ausência de incidente: os rollouts 0/1 conservaram pods antigos saudáveis. Sem acesso ao vídeo Loom privado, a tag foi introduzida diretamente para reproduzir o sintoma; não se atribui conteúdo ao vídeo.

## Parte B

Acerto: 10/10.

| Frase | Esperado | Obtido |
|---|---|---|
| o pod do nyx-prod não sobe | triagem-cluster | triagem-cluster |
| por que esse deployment está 0/3 | triagem-cluster | triagem-cluster |
| o service do nyx-stg não tem endpoint | triagem-cluster | triagem-cluster |
| revisa esse deployment antes de eu subir | manifests-metacortex | manifests-metacortex |
| esse manifesto está no padrão da casa? | manifests-metacortex | manifests-metacortex |
| cria um Deployment novo do zero pra mim | manifests-metacortex | manifests-metacortex |
| esse manifesto não sobe no cluster | esclarecer | esclarecer |
| o Service do nyx não está entregando tráfego | triagem-cluster | triagem-cluster |
| o que é um DaemonSet? | nenhuma | nenhuma |
| provisiona uma VM nova no Construct pro cliente orion | nenhuma | nenhuma |

## Parte C

| Caso | Modo | Entrada tokens | Cache tokens | Saída tokens | Tempo s |
|---|---|---:|---:|---:|---:|
| nyx-prod | com-skill | 58882 | 13696 | 232 | 9.135 |
| nyx-prod | sem-skill | 58247 | 13696 | 217 | 9.781 |
| nyx-stg | com-skill | 46967 | 13696 | 203 | 7.995 |
| nyx-stg | sem-skill | 46332 | 22656 | 184 | 8.04 |
| manifesto | com-skill | 25177 | 13696 | 1016 | 26.759 |
| manifesto | sem-skill | 24082 | 22656 | 382 | 12.843 |

As respostas de nyx-prod e nyx-stg com e sem skill acertaram a causa. Com skill não houve economia demonstrada de tokens: a entrada aumentou 635 tokens nos dois incidentes. Para o manifesto, com skill trouxe mais regras da casa e recomendações, com maior saída e tempo. Saída ruim: com skill afirmou que as quatro chaves de label não estavam fornecidas; elas existem no script mas não foram incluídas no prompt restrito. O relatório do agente principal usa os arquivos completos e corrige essa lacuna. A expressão "causa provável" no OOM é prudente para sizing sob carga; OOMKilled/137 e limite são observações. Nenhuma sugestão foi aplicada durante as triagens.

Respostas, entradas, eventos Codex, usage e tempo por execução ficam em [exemplos](../../ticket-02-triagem-no-cluster/exemplos/); `versoes-prompts.json` identifica o conteúdo das skills usado antes de atualizar a curadoria. `avaliar_codex.py` lê saídas MCP reais e recusa registros de erro.
