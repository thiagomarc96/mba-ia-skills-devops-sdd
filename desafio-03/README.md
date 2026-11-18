# Desafio 03 — Skills de DevOps e SDD

Estudo pessoal com execução em 18/11/2026 no cluster local `kind-desafio03`. Os tickets T01, T02 e T04 têm evidências coletadas da API Kubernetes. Os dois projetos KubeDev usados são kube-news/nyx e fake-shop/orion, em namespaces separados.

- [T01: escrita, conferência e cobertura Trivy medida](ticket-01-padrao-de-manifests/README.md).
- [T02: MCP de leitura, três chamados e medições](ticket-02-triagem-no-cluster/README.md).
- [T03: inventário de VM](ticket-03-inventario-de-vm/README.md).
- [T04: dashboard e oito cenários coletados](ticket-04-dashboard-do-cluster/README.md).
- [Reprodução do laboratório e segurança](../laboratorio/README.md).
- [Índice das evidências e validações](../evidencias/README.md).

O laboratório utiliza imagens públicas por digest e credenciais efêmeras fora do Git. Exceções ao padrão Metacortex e limitações de produção constam na curadoria de cada ticket. O cluster é removido no fechamento; a confirmação fica em `evidencias/preparo/limpeza.txt`.

A estrutura contém este README e as quatro pastas dos tickets. Configuração MCP, manifests, scripts, specs e curadoria ficam no respectivo ticket; evidências compartilhadas e preparo permanecem na raiz do repositório. Os requisitos fornecidos abrangem os dois modos de manifests, três chamados MCP, dez rotas, comparativos, inventário SSH e dashboard com dois projetos e três falhas de acesso. T03 e T04 têm as mudanças OpenSpec arquivadas e as specs consolidadas.
