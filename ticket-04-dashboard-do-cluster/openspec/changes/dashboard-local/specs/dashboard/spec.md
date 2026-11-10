# ADDED Requirements

## Requirement: contexto fixo e leitura

O dashboard MUST capturar o contexto corrente ao iniciar e usar esse nome em cada consulta. MUST permitir somente leituras dos seis recursos declarados e servir apenas em loopback.

### Scenario: contexto alterado externamente
GIVEN contexto A capturado, WHEN o current-context passa a B, THEN as consultas continuam com --context A até reiniciar.

### Scenario: entrada indevida
WHEN o namespace contém argumento ou caracteres inválidos, THEN nenhuma consulta é feita e a resposta é 400.

## Requirement: visão do namespace

O dashboard MUST exibir namespaces, pods, deployments, services e eventos, com filtro de namespace e busca por nome.

### Scenario: falhas e campos ausentes
GIVEN um pod Running em CrashLoopBackOff com OOMKilled anterior, THEN ambos os motivos e reinícios são exibidos. GIVEN deployment sem readyReplicas, THEN prontos é zero. GIVEN slice sem endpoints, THEN o service aparece sem endpoint pronto.

### Scenario: permissão parcial
GIVEN leitura de EndpointSlice negada, THEN os outros blocos permanecem disponíveis e endpoints aparecem desconhecidos, nunca zero por inferência.

## Requirement: falhas úteis

O dashboard MUST apresentar erro legível para contexto ausente, kubectl indisponível, timeout, autenticação e autorização, sem stack trace ou stderr cru. MUST usar atualização manual.

### Scenario: cluster inacessível
WHEN a chamada falha ou excede o prazo, THEN a UI apresenta o erro e permite nova atualização; não apresenta dados inexistentes como saudáveis.

## Requirement: validação honesta

Testes sintéticos MUST ser identificados como tais. Validação com dois workloads, RBAC real e credencial expirada permanece pendente enquanto não executada.
