---
name: triagem-cluster
description: Diagnosticar indisponibilidade de workloads já aplicados a um cluster Kubernetes por leituras do mcp-server-kubernetes. Use para pod que não sobe, deployment sem réplicas prontas, Service sem endpoint ou tráfego. Não use para criar/revisar YAML antes de aplicar, explicar conceitos ou provisionar VM. Em "esse manifesto não sobe", esclareça se houve aplicação e qual o erro.
---

# Triagem no cluster

## Limite absoluto

Somente leitura, mesmo que a ferramenta permita escrita. Não aplicar, editar, apagar, escalar, reiniciar, executar comando dentro do pod ou corrigir recursos. Não ler Secrets. A preparação do laboratório é etapa externa, nunca parte da triagem. Usar mcp-server-kubernetes em modo não-destrutivo, sem habilitar permissões adicionais. Se não houver ferramenta de leitura adequada, parar e informar o limite.

## Entradas

Sintoma, namespace e objeto quando conhecido. Confirmar contexto de laboratório autorizado. Não trocar contexto nem investigar outros clientes sem necessidade. Listar as ferramentas realmente disponíveis; não inventar nome de ferramenta MCP.

## Método

1. Começar pelo recurso relacionado ao sintoma. Para pod/deployment indisponível, ler workload, pods e eventos recentes do namespace. Para tráfego/503, ler Service, EndpointSlices, seletores e prontidão dos pods.
2. Distinguir phase de pod de estado dos containers. Examinar initContainers, waiting, terminated, lastState e restartCount. Consultar evento e estado antes de pedir logs; restringir logs ao pod/container relevante e à janela do incidente.
3. Reinício: cruzar motivo da última terminação, código, limite de memória e eventos. OOMKilled/137 mais limite baixo sustenta hipótese de memória; CrashLoopBackOff sozinho não prova a causa. Considerar banco saudável separadamente.
4. ImagePullBackOff/ErrImagePull: cruzar imagem exata com evento de pull. Não confundir tag inexistente, credencial, DNS ou rate limit; não tentar criar pull secret nem alterar tag. A causa só está identificada quando a mensagem da API sustenta a classificação.
5. Service sem endpoint: cruzar selector com labels dos pods e condições das EndpointSlices. Diferenciar ausência de pods selecionados de pods selecionados não prontos. Falta de permissão é dado desconhecido, não conjunto vazio.
6. Cruzar no mínimo duas fontes pertinentes antes de concluir. Separar o recurso com defeito dos recursos saudáveis do mesmo namespace. Não continuar coletando logs sem necessidade depois de identificar a causa.
7. Entregar sintoma, evidências/localizações, causa ou hipótese, grau de confiança e próxima ação sugerida. Não executar a sugestão. Se não houver evidência suficiente, dizer o que falta em vez de escolher a causa do enunciado.

## Segurança dos resultados

Omitir tokens, credenciais e conteúdo sensível eventualmente encontrado em logs ou eventos. Não exportar kubeconfig. Registrar apenas os trechos mínimos necessários ao diagnóstico.
