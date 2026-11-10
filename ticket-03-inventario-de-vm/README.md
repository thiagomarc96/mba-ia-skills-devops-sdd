# Inventário de VM

Coleta por SSH e comparação com o baseline, sem instalar agente ou corrigir o host.

## Executar

Pré-requisitos: Python 3.10+ e OpenSSH na estação; Python 3, systemd, iproute2 e OpenSSH no Linux. A chave do host precisa estar previamente validada no known_hosts. Não desative essa validação.

```sh
python -m pip install -r requirements.txt
python inventario.py --host 10.42.7.14 --usuario operador --chave /caminho/chave --saida saida
```

A chave é recebida por caminho, nunca por conteúdo. JSON e Markdown são gravados no diretório local informado. Retornos: 0 conforme, 1 desvio, 2 não verificado sem desvio, 3 falha de entrada/conexão. Havendo desvio e coleta parcial, retorna 1 e preserva ambos no relatório.

## Artefatos

- [Brainstorm](brainstorm.md), [especificação](spec.md) e [mudança OpenSpec](openspec/changes/inventario-ssh/).
- [Coletor](coletor.py), [CLI e avaliação](inventario.py), [baseline](baseline.yaml).
- [Testes unitários](test_inventario.py): `python -m unittest -v`.
- [Curadoria](curadoria.md).

## Validação

Gere os exemplos com `python gerar_exemplos.py`: [conforme](exemplos/conforme.md), [desvio](exemplos/desvio.md), [parcial](exemplos/parcial.md), [host inacessível](exemplos/host-inacessivel.md) e [repetição](exemplos/repeticao.md). Cada cenário inclui JSON, Markdown e código de saída.

O gerador usa a [fixture de inventário](fixtures/inventario.json). A repetição altera apenas o instante da coleta. Testes: `python -m unittest -v`.
