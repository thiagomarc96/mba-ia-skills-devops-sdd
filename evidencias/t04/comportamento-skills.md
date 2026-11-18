# Comportamento observado das skills nas falhas

Todas as consultas são ao contexto `kind-desafio03`; o servidor e os certificados estão mascarados nos registros de falha. Preparação e injeção são etapas separadas das skills.

| Falha provocada | T01: conferência local | T02: chamada MCP e decisão |
|---|---|---|
| Porta incorreta no kubeconfig isolado | 19 achados, retorno 1; não depende da API | Erro de conexão recusada; parar a coleta e informar acesso indisponível, sem concluir que pods/Endpoints estão ausentes. |
| Token ligado ao Secret removido | 19 achados, retorno 1 | API HTTP 401, MCP informa autenticação exigida; parar e solicitar credencial válida fora da skill, sem trocar por conta mais ampla. |
| platform-ro sem acesso a EndpointSlice em acesso-parcial | 19 achados, retorno 1 | API HTTP 403, MCP informa Forbidden; estado dos endpoints desconhecido. Não afirmar mismatch nem inexistência de destinos sem conseguir ler a fonte. |

O comportamento do T01 está registrado em `t01-falhas-acesso.json`; respostas brutas dos testes HTTP em `falhas-http.json`; respostas MCP em `cluster-indisponivel-mcp.json`, `credencial-expirada-mcp.json` e `permissao-negada-mcp.json`. Essas três consultas MCP de falha não efetuaram correções nem leitura de Secrets. As decisões acima aplicam o método da skill aos erros observados, sem inventar uma causa do workload.

Os oito snapshots em `ticket-04-dashboard-do-cluster/exemplos/fixtures` passaram pelo backend HTTP. Nas falhas globais, a API local retorna HTTP 200 contendo seis erros por recurso, enquanto a API Kubernetes retorna 401 ou sequer aceita conexão. No acesso parcial, os pods permanecem visíveis e os endpoints ficam desconhecidos. Os testes não usam credencial de escrita como fallback.

Na operação normal, o roteamento explícito foi T01 para escrita/conferência de YAML e T02 para recursos já aplicados. A matriz separada teve 10/10 acertos, incluindo pedido ambíguo encaminhado para esclarecimento e dois pedidos fora do escopo. Não há inferência de disparos espontâneos fora das sessões registradas.
