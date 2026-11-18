# Inventário de VM

Coleta por SSH e comparação com o baseline, sem instalar agente ou corrigir o host.

## Executar

Pré-requisitos: Python 3.10+ e OpenSSH na estação; Python 3, systemd, iproute2 e OpenSSH no Linux. A chave do host precisa estar previamente validada no known_hosts. Não desative essa validação.

```sh
python -m pip install -r requirements.txt
python inventario.py --host 10.42.7.14 --usuario operador --chave /caminho/chave --known-hosts /caminho/known_hosts --porta 22 --saida saida
```

A chave é recebida por caminho, nunca por conteúdo. JSON e Markdown são gravados no diretório local informado. Retornos: 0 conforme, 1 desvio, 2 não verificado sem desvio, 3 falha de entrada/conexão. Havendo desvio e coleta parcial, retorna 1 e preserva ambos no relatório.

## Artefatos

- [Brainstorm](brainstorm.md), [especificação](spec.md) e [mudança OpenSpec](openspec/changes/archive/2026-11-18-inventario-ssh/).
- [Coletor](coletor.py), [CLI e avaliação](inventario.py), [baseline](baseline.yaml).
- [Testes unitários](test_inventario.py): `python -m unittest -v`.
- [Curadoria](curadoria.md).

## Validação em SSH real

Em 18/11/2026, o coletor acessou um servidor OpenSSH em container Ubuntu 24.04, publicado somente em loopback com porta efêmera. Chave privada e known_hosts ficaram em diretório temporário fora do Git. A chave pública do servidor foi obtida pelo Docker local e validada pelo OpenSSH com StrictHostKeyChecking=yes.

- [Primeira coleta JSON](../../evidencias/t03/primeira/inventario.json) e [Markdown](../../evidencias/t03/primeira/inventario.md), retorno [1](../../evidencias/t03/primeira.codigo.txt).
- [Segunda coleta JSON](../../evidencias/t03/segunda/inventario.json) e [Markdown](../../evidencias/t03/segunda/inventario.md), retorno [1](../../evidencias/t03/segunda.codigo.txt). As duas execuções SSH têm instantes distintos e vereditos iguais.
- [Host inacessível JSON](../../evidencias/t03/host-inacessivel.json) e [Markdown](../../evidencias/t03/host-inacessivel.md), retorno [3](../../evidencias/t03/host-inacessivel.codigo.txt): o servidor foi parado e a mesma porta recusou conexão TCP e SSH.
- [Registro da execução](../../evidencias/t03/execucao.json) e [remoção do container](../../evidencias/t03/limpeza.txt).

As coletas apresentam 6 regras conformes, 2 desvios (swap e login root) e 3 regras não verificadas (serviços ativos/proibidos e NTP). O container compartilha o kernel e a visão de swap do host; não executa systemd como PID 1. Os dados não demonstram conformidade de uma VM de produção. A falha SSH não gera relatório de conformidade: o JSON e o MD desse caso são registros do ensaio.

Para reproduzir, a partir da raiz: `python3 laboratorio/ssh/executar.py`. Requer Docker, OpenSSH, Python e PyYAML; o script cria e remove seu próprio container. O baseline não é relaxado para fazer o laboratório passar. Fixtures e interceptação de subprocessos ficam restritas aos testes unitários temporários, sem compor as evidências de execução. [Validações](../../evidencias/validacao.txt).
