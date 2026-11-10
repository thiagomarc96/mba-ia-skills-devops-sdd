## ADDED Requirements

### Requirement: Inventário somente de leitura
O sistema SHALL coletar uma VM por SSH sem instalar, modificar ou corrigir o host e sem revelar a chave privada.

#### Scenario: Coleta parcial
- **WHEN** uma consulta não possui permissão
- **THEN** o campo deve ser indisponível e a regra nao_verificado, mantendo as outras consultas.

### Requirement: Relatórios consistentes
O sistema SHALL avaliar todas as regras do baseline e gerar JSON e Markdown do mesmo resultado.

#### Scenario: Desvio
- **WHEN** um valor diverge do baseline
- **THEN** a regra contém esperado, encontrado, desvio e a severidade declarada.

#### Scenario: Falha de conexão
- **WHEN** SSH não alcança o host ou rejeita a autenticação
- **THEN** a CLI retorna 3 com mensagem sanitizada e não emite relatório de conformidade.
