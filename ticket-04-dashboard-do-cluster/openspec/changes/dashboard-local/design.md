# Decisões

As alternativas e seus ganhos/perdas estão no [brainstorm](../../../brainstorm.md).

Backend HTTP local com Python e UI HTML/JavaScript sem build. O backend captura `kubectl config current-context` uma vez e acrescenta `--context` a todas as consultas. Não usa shell, exec remoto, proxy, apply, delete ou scale. Os únicos recursos permitidos são namespaces, pods, deployments, services, endpointslices.discovery.k8s.io e events. O namespace passa por validação antes de virar argumento.

EndpointSlice é agregado pelo rótulo kubernetes.io/service-name. Endpoints sem endereço ou com ready=false não contam como prontos. Ready ausente é contado como desconhecido, não como comprovação de saúde. Services ExternalName são identificados como DNS externo, não recebem falsa falha por ausência de slice.

Erros são classificados em autorização, autenticação, conexão/timeout e resposta inválida; stderr não é retornado ao navegador. Cada tipo de recurso falha independentemente. A falta de autorização nas slices significa endpoints desconhecidos.

Eventos são ordenados pelo horário disponível, com no máximo 50 exibidos. A busca por nome acontece sobre os dados carregados no namespace. A UI usa textContent, sem interpolar HTML com dados do cluster. Requisições simultâneas são evitadas na UI, e o servidor é sequencial. Apenas GET é implementado, com validação do cabeçalho Host e sem CORS.

Limite: fixar o nome do contexto não congela edições no próprio kubeconfig. Não editar suas definições enquanto a aplicação estiver aberta. A autenticação por plugin exec do kubeconfig pode executar o plugin já configurado pelo operador; a aplicação não cria credenciais ou altera esse arquivo.
