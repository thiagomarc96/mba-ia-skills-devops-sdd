# Triagem no cluster

Skill: [triagem-cluster](skill/SKILL.md). Alcance: [mcp-server-kubernetes](https://github.com/flux159/mcp-server-kubernetes), em modo não-destrutivo.

## Curadoria e origem

Método preparado com Codex a partir dos três chamados do enunciado. Fixa o ponto de entrada por sintoma, o cruzamento de fontes, a parada ao identificar causa e a proibição de escrita. O agente decide qual objeto/container examinar e quanto aprofundar, dentro do namespace e do objetivo. Não fixa nomes de ferramentas MCP, que devem ser descobertos no servidor instalado.

As permissões devem combinar modo não-destrutivo e credencial de leitura com get/list/watch dos recursos necessários. Logs precisam de pods/log. Não conceder acesso a Secrets ou exec. O texto da skill é uma defesa adicional, não substitui RBAC.

## Chamados: hipóteses da leitura dos manifests

| Chamado | Hipótese | Evidência necessária para confirmar |
|---|---|---|
| nyx-prod reinicia | Limite de memória de 24Mi no kube-news | OOMKilled/código 137, eventos e limite; estado do banco separadamente |
| orion-stg não troca pod | Falha ao obter imagem/tag anunciada | ErrImagePull/ImagePullBackOff e mensagem exata do registry no evento |
| nyx-stg responde 503 | Selector `app: nyx-api` diferente do label `app: nyxapi` | Service, labels dos pods prontos e EndpointSlice sem destinos |

## Matriz de roteamento esperada

| Pedido | Rota esperada |
|---|---|
| o pod do nyx-prod não sobe | triagem-cluster |
| por que esse deployment está 0/3 | triagem-cluster |
| o service do nyx-stg não tem endpoint | triagem-cluster |
| revisa esse deployment antes de eu subir | manifests-metacortex |
| esse manifesto está no padrão da casa? | manifests-metacortex |
| cria um Deployment novo do zero pra mim | manifests-metacortex; pedir projeto/cliente/ambiente se faltarem |
| esse manifesto não sobe no cluster | Esclarecer: erro no arquivo, erro de apply ou workload já aplicado? |
| o Service do nyx não está entregando tráfego | triagem-cluster |
| o que é um DaemonSet? | Nenhuma; explicação geral |
| provisiona uma VM nova no Construct pro cliente orion | Nenhuma; fora do escopo |

## Medição

Casos selecionados: revisão do manifesto barrado e triagem do Service sem endpoint. Comparar a mesma entrada/modelo/configuração, em sessões limpas, com e sem skill. Registrar saída, acerto causal/cobertura de regras, ferramentas acionadas, duração e uso/custo retornado pelo provedor. Custo indisponível deve permanecer indisponível, não estimado como medido.

Roteamento e comparação acima são critérios de avaliação, não resultados de execução. As saídas reais dos três chamados e as medições não foram produzidas.
