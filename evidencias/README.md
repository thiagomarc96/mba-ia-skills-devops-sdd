# Evidências da execução de 18/11/2026

Tudo neste diretório provém de comandos executados no host ou de análise identificada dos respectivos resultados. Credenciais e kubeconfigs privados ficaram fora do Git. Os endereços do servidor e certificados estão mascarados nas evidências de acesso.

| Ticket | Evidências principais |
|---|---|
| Preparo | `preparo/instalacao-repeticao.txt` (checksums e versões), `preparo/kind-create.txt`, `preparo/npm-pack.txt`, logs de pulls; primeira tentativa de download 404 preservada. |
| T01 | `t01/trivy-antes.txt`, `t01/trivy-barrado.json`, `t01/skill-conferencia.json`, `t01/skill-escrita.json`, `t01/trivy-depois.json`, `t01/cobertura.md` e JSON com 19 famílias; `kubectl-get-all-*.txt`; `http-funcional-dev.json`; saídas ruins e correções de startup. |
| T02 A | `t02/mcp-tools.json` e `t02/{nyx-prod,orion-stg,nyx-stg}-mcp.json`: 15 consultas reais por stdio, 5 por chamado, com request/resposta/tempo. |
| T02 proteção | `t02/mcp-escrita-negada.json`, `rbac-escrita-negada.txt`, `rbac-secrets-negado.txt` e `ausencia-escrita.txt`. |
| T02 B/C | `t02/avaliacao.md`, `t02/avaliacao-codex.txt`; respostas e eventos do Codex em `ticket-02-triagem-no-cluster/exemplos`, 10 rotas e 7 análises. |
| T04 | `t04/falhas-http.json`, três `*-mcp.json` de erro, `t01-falhas-acesso.json`, `comportamento-skills.md`, `coleta-dashboard.txt`; oito snapshots em `ticket-04-dashboard-do-cluster/exemplos/fixtures`. |
| Validação | `validacao.txt`: 36 testes unitários (6+19+11), geradores T03, compilação Python, sintaxe JavaScript/Bash e diff. `revisao-final.json`: contratos das evidências, links, tamanho de skill e busca por segredos em memória. |
| Fechamento | `preparo/limpeza.txt`: remoção do kind, listagem final de clusters e `docker ps` filtrado pelo nome do laboratório. |

A API Kubernetes confirmou 401 para token revogado e 403 para permissão ausente. O erro de conexão veio de uma porta inválida em uma cópia privada do kubeconfig. Na triagem normal, pods antigos permaneceram saudáveis durante os rollouts bloqueados, o que está explicitado nos relatórios. Recomendações não são execução de correção.

Limitações: uma amostra por comparação de modelo; cache varia; custo monetário não fornecido; sizing de pico, HA/durabilidade do banco e adaptação das probes do fake-shop continuam fora da conformidade de produção do laboratório. Esses limites não são convertidos em aprovação. O inventário T03 teve validação unitária com sua fixture local, preservando seu escopo.

Apenas a formatação dos logs de texto foi normalizada (LF, espaços finais e linhas vazias finais); `normalizacao-logs.json` guarda os hashes originais e finais. Nenhum conteúdo de diagnóstico foi substituído.
