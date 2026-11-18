# Curadoria

O dashboard mantém a implementação local mínima: seis recursos permitidos, somente leitura, loopback e contexto fixado. Não há banco próprio nem funcionalidade de ajuste. Brainstorm e OpenSpec preservam o histórico de decisões anterior à implementação.

Em 18/11/2026, kube-news e fake-shop foram executados em namespaces separados com os manifests do T01. A coleta de integração passou pelo backend HTTP e consultou Kubernetes usando a SA platform-ro. Oito snapshots reais foram registrados; `coletar.py` exige kubeconfigs externos e verifica cada resultado. Testes unitários continuam isolados para validar segurança, timeouts, tratamento de JSON e semântica dos estados.

Uma EndpointSlice que não pode ser lida é desconhecida; ela não equivale a zero endpoints. EndpointSlice com ready ausente não prova prontidão. ExternalName é apresentado como DNS externo. Falta de contexto ou falha de autenticação aparece como erro, sem credenciais ou stack trace no HTTP. Os eventos não provam estado atual sozinhos: a triagem diferenciou eventos antigos de pods atuais.

A captura confirmou falhas reais de conexão, token revogado (401) e permissão (403). O dashboard retornou HTTP 200 para a resposta de estado com os erros explicados por recurso; esse 200 não significa sucesso da consulta ao cluster. A implementação também distingue phase Running de OOM anterior/reinícios.

T01 só trabalhou com YAML; T02 usou somente leituras MCP. Nas falhas de acesso, T02 interrompe o diagnóstico causal e informa a lacuna; T01 ainda consegue conferir o YAML local, sem inferir estado do cluster. Detalhes e registros: [comportamento das skills](../../evidencias/t04/comportamento-skills.md).

A interface usa textContent/replaceChildren para tratar dados como texto. [Validações](../../evidencias/validacao.txt).
