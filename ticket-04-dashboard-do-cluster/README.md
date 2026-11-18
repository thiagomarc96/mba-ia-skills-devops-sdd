# Dashboard do cluster — T04

Dashboard local de leitura em Python/HTML/JS, com kubectl no contexto do kubeconfig. Exibe namespaces, pods, deployments, Services/EndpointSlices e os 50 eventos recentes, com busca e atualização manual.

```sh
export KUBECONFIG=/caminho/privado/ro.config
python3 dashboard.py --context kind-desafio03
# http://127.0.0.1:8088 ; encerrar com Ctrl+C
python3 -m unittest -v
```

Sem `--context`, fixa o contexto corrente ao iniciar. No laboratório todas as consultas foram explicitamente fixadas em `kind-desafio03`. Namespace validado, lista fechada de recursos e comandos get, timeouts de 10/15 segundos, sem Secrets/exec/shell ou rota de escrita. Servidor somente em loopback, sem CORS. Nome do contexto fixado não impede edição externa do próprio kubeconfig.

O coletor [coletar.py](coletar.py) usa o mesmo adaptador Kubernetes real e atravessa o backend HTTP. Os oito arquivos em [exemplos/fixtures](exemplos/fixtures/) contêm respostas da API, consultas feitas, resposta do backend e horário de coleta. Esses dados são snapshots para revisão, sem replay de um cluster.

```sh
export KUBECONFIG_RO=/caminho/privado/ro.config
export KUBECONFIG_REVOGADO=/caminho/privado/revoked.config
export KUBECONFIG_INDISPONIVEL=/caminho/privado/unavailable.config
python3 coletar.py
```

| Cenário real | Verificação |
|---|---|
| nyx-dev / orion-dev | Apps e PostgreSQL prontos, nenhum erro de coleta. |
| nyx-prod | OOMKilled em pod novo, revisões antigas preservadas. |
| orion-stg | ImagePullBackOff/ErrImagePull na tag nova, pods antigos prontos. |
| nyx-stg | API Ready, Service sem endpoint pronto por selector. |
| acesso-parcial | platform-ro lê pods e demais recursos; EndpointSlice retorna 403 e fica desconhecida. |
| credencial-expirada | Token ligado a Secret revogado, API retorna 401; seis erros de autenticação na tela. |
| cluster-indisponivel | Porta inválida em cópia privada do kubeconfig, conexão recusada; seis erros de conexão. |

O cenário de credencial usa revogação real, não espera o relógio de expiração do token. A porta incorreta afeta apenas o kubeconfig isolado; o cluster continuou disponível para as demais consultas. Os códigos HTTP brutos e comportamento das skills estão em [evidencias/t04](../evidencias/t04/).

[Brainstorm](brainstorm.md), [proposta](openspec/changes/dashboard-local/proposal.md), [design](openspec/changes/dashboard-local/design.md), [spec](openspec/changes/dashboard-local/specs/dashboard/spec.md), [tarefas](openspec/changes/dashboard-local/tasks.md) e [curadoria](curadoria.md). Os READMEs registram as limitações sem equiparar Ready a saúde funcional ou erro de permissão a conjunto vazio.
