---
name: manifests-metacortex
description: Criar ou revisar arquivos de manifests Kubernetes segundo o padrão Metacortex, antes da aplicação. Use para pedido explícito de escrita/revisão de YAML. Não use para diagnosticar estado de cluster, conceitos gerais ou provisionamento de VM. Se "não sobe" não distinguir arquivo de recurso aplicado, esclareça primeiro.
---

# Manifests Metacortex

## Limite

Escreva ou confira arquivos; nunca aplique recursos. Não leia nem exponha credenciais. A aprovação do script não garante conformidade integral.

## Fluxo

1. Identifique modo (escrever/conferir), cliente, ambiente, projeto e arquivos. Em pedido ambíguo, pergunte se o problema está no YAML ou no cluster em execução.
2. Leia `references/criterios.md` e o código do workload: porta, endpoints, dependências, variáveis, inicialização/migração, paths de escrita e encerramento. Não invente endpoints ou propriedades da imagem.
3. Confira os arquivos com `trivy config DIRETORIO` antes de criar novos controles. Registre versão, comando e saída reais se executado. Se não puder executar, marque como não verificado.
4. Execute `python scripts/conferir.py ARQUIVO.yaml` para o recorte próprio da Metacortex. Não repita a implementação dos controles já demonstrados pelo Trivy; revise a divisão após medir cobertura.
5. No modo escrita, gere o mínimo de objetos necessários. Segredos entram por `secretKeyRef`, sem Secret preenchido nem senha em comentário. Não trate tag como imutável sem evidência do registry. Informe dependências não provisionadas.
6. No modo conferência, relate por regra: achado, localização, impacto e proposta, sem alterar o arquivo sem pedido. Confira seletores entre os objetos e as variáveis contra o código.
7. Separe obrigatório/proibido/recomendado e verificado/não verificado. Não declare aprovado se houver decisão sem base, dependência pendente ou regra obrigatória não verificada.

## Decisões de aplicação

`kube-news`: confirmar `/health` e `/ready` no commit analisado e declarar a limitação de não verificarem banco. `fake-shop`: não inventar `/health`; analisar migração no start e caminhos graváveis. TCP só verifica processo/socket e não atende silenciosamente a exigência de endpoint funcional. Se a aplicação não fornece o contrato exigido, explicar o bloqueio e propor alteração específica ou exceção formal, sem fingir conformidade. Dimensionamento requer consumo observado; valor estimado permanece não verificado.

## Entrega

Arquivos escritos ou relatório de conferência; referências ao código consultado; verificações executadas e não executadas; decisões/limitações. Não preencher logs, custo ou duração retroativamente.
