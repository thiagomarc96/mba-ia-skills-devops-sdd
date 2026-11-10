# Dashboard do cluster

Dashboard local somente leitura, em Python e HTML/JS sem dependências externas. Exibe namespaces, pods, deployments, services/EndpointSlices e os 50 eventos mais recentes do namespace. Busca por nome e atualização manual.

## Executar

Pré-requisitos: Python 3.10+, kubectl e kubeconfig já configurado. A aplicação consulta o contexto corrente ao iniciar e fixa seu nome até ser encerrada. Não editar a definição desse contexto durante o uso.

```sh
python dashboard.py
# Abra http://127.0.0.1:8088
```

Outra porta: `python dashboard.py --porta 8089`. Encerrar com Ctrl+C. Na tela, digite ou escolha o namespace e clique em Atualizar. Os nomes dos namespaces são sugeridos quando a conta permite listá-los; sem essa permissão é possível digitar um namespace conhecido.

A autenticação fica a cargo do kubectl, incluindo plugins exec existentes. O programa não pede, armazena ou imprime credenciais. Credencial expirada, cluster indisponível e permissão parcial aparecem na tela. Falha de leitura de EndpointSlice significa estado desconhecido, não ausência de endpoints.

## Somente leitura

Comandos fixos: `kubectl config current-context` e `kubectl --context CONTEXTO get RECURSO -o json`, com timeout. Os seis recursos permitidos estão em `RESOURCES`; o namespace é validado. Nenhum comando de escrita, shell, exec remoto ou rota de mutação. Servidor apenas em 127.0.0.1 e sem CORS. Estado Ready reportado pela API não equivale a saúde funcional.

## Processo e verificação

- [Brainstorm e alternativas](brainstorm.md), anterior ao código.
- [Proposta](openspec/changes/dashboard-local/proposal.md), [design](openspec/changes/dashboard-local/design.md), [spec](openspec/changes/dashboard-local/specs/dashboard/spec.md) e [tarefas](openspec/changes/dashboard-local/tasks.md), escritos antes da implementação.
- [Curadoria e limites](curadoria.md).

```sh
python -m unittest -v
```

## Exemplos

```sh
python simular.py
# Abra http://127.0.0.1:8089
python simular.py --gerar-exemplos
```

Os namespaces representam oito cenários: kube-news e fake-shop prontos; CrashLoopBackOff/OOMKilled; ImagePullBackOff; Service sem endpoint; acesso parcial; credencial expirada; cluster indisponível. Entradas e respostas do backend estão em [exemplos/fixtures](exemplos/fixtures/).
