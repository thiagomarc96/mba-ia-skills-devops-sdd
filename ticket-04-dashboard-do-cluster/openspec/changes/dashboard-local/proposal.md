# Proposta — dashboard local somente leitura

## Objetivo

Reduzir a consulta inicial do plantão a uma tela local com namespaces, pods, deployments, services, endpoints e eventos. A entrega terá apenas filtro de namespace, busca por nome e atualização manual.

## Escopo

Python 3.10+ e biblioteca padrão; kubectl instalado pelo operador. Contexto corrente capturado ao iniciar, sem seletor de cluster. A aplicação permanece aberta mesmo se a captura do contexto falhar, apresentando erro claro. Nesse caso será necessário reiniciar após corrigir a configuração.

Sem escrita no cluster, instalação de agentes, métricas adicionais, histórico ou autenticação própria. Interface limitada a 127.0.0.1.

## Validação

Testes unitários para transformação dos dados, contexto fixo e restrição dos comandos. Integração com dois workloads, falhas de acesso e arquivamento conforme a lista de tarefas.
