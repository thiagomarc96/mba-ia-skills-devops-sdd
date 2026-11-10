# Dashboard do cluster — brainstorm

## Menor entrega que atende

Aplicação local com filtro de namespace, busca por nome e botão atualizar. Mostrar namespaces, pods (estado, reinícios e motivo), deployments (prontos/desejados), services (presença de endpoint) e eventos recentes. Sem multicluster, alteração de recurso, login próprio, histórico ou métricas adicionais.

## Decisões propostas e alternativas

| Decisão | Escolha | Alternativa 1 | Alternativa 2 |
|---|---|---|---|
| Linguagem/stack | Python e HTML/JS simples: pouca instalação e familiar para infraestrutura; exige cuidar do servidor local | React/Node: componentes ricos, mas build e dependências desnecessários | Go: binário único, mas curva de manutenção e compilação maiores |
| Acesso ao cluster | kubectl como subprocesso com lista fixa de leituras: reutiliza autenticação; custo de processos e parsing | Cliente oficial Python: tipagem/API direta, mas dependência e autenticação precisam ser validadas | HTTP direto: controle fino, mas reimplementa autenticação e TLS |
| Atualização | Sob demanda: comportamento explícito e menor carga; dado fica antigo até atualizar | Intervalo fixo: mais atual, mas consulta mesmo sem necessidade | Watch: baixa latência, mas reconexão e consistência aumentam o escopo |
| Endpoints | EndpointSlice: API atual, permite agregação por service; exige tratar múltiplas slices | Endpoints: simples, mas depreciado e limitado | Inferir pelos labels de pods: menos consulta, mas não representa a decisão real do controlador |
| Primeira fatia | Todos os objetos mínimos e erros parciais, somente leitura | Somente pods: menor esforço, mas não atende o enunciado | Métricas/logs/ações: mais operação, mas adiciona escopo não pedido |

## Garantias a especificar

- Capturar o contexto corrente ao iniciar; fixar esse contexto nas consultas. Mudança externa não troca o destino durante a execução.
- Escutar apenas em loopback. Nenhuma rota de escrita; verbos/comandos construídos por lista permitida, sem shell e sem comando fornecido pela UI.
- Timeout por consulta. Um recurso proibido não esconde os demais; mostrar erro por bloco. Distinguir credencial expirada, acesso negado e cluster indisponível sem exibir credenciais.
- Estado de container tem precedência para explicar CrashLoopBackOff/OOMKilled; phase Running não significa saúde. Somar reinícios dos containers; tratar campos opcionais e init containers.
- readyReplicas ausente representa zero. EndpointSlice sem endereço pronto representa sem endpoint, mas erro de autorização representa desconhecido, não vazio.
- Pod Ready não prova saúde funcional da aplicação. Mostrar estado reportado pela API, sem promessa de disponibilidade ponta a ponta.
- Renderizar nomes, mensagens e eventos como texto, nunca HTML fornecido pelo cluster.

## Validação prevista

Cluster real com pelo menos dois workloads em namespaces separados, manifests derivados do ticket 01. Evidência da tela, busca e filtro; cluster inacessível; credencial inválida; leitura parcial negada; contexto fixo; ausência de writes. Registrar separadamente testes unitários com fixtures e evidências reais.

Há uma tensão de laboratório a resolver explicitamente: o padrão exige registry interno fictício, enquanto os workloads públicos são fornecidos para laboratório. Não alegar conformidade do registry se for necessário usar uma adaptação local.

Durante o projeto, registrar quais skills dispararam espontaneamente, manualmente ou fora de escopo. Não preencher esse registro antes das sessões reais.

## Implementação

Proposta, design, requisitos e tarefas em `openspec/changes/dashboard-local/`.
