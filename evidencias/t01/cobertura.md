# Cobertura medida e curadoria — 18/11/2026

Trivy 0.69.3, corpus fixo [manifesto barrado](../../ticket-01-padrao-de-manifests/exemplos/manifesto-barrado.yaml). São 18 ocorrências, 17 IDs distintos. O verificador inicial tinha 20 ocorrências/7 regras; removido o controle duplicado de latest (KSV-0013), o final tem 19 ocorrências/6 regras.

Das 19 famílias do padrão, 14 têm falha ou recomendação ausente neste corpus: Trivy cobre 3/14 (21,43%); somente skill cobre 11/14 (78,57%): 6 pelo script e 5 por revisão. Os demais 5 itens atendem ou dependem de informação/observação. Contagem por família evita comparar 18 checks do Trivy com 19 ocorrências do script como se fossem equivalentes. Não é estimativa da cobertura global do produto.

| Regra | Estado | Responsável observado | Evidência/limite |
|---|---|---|---|
| 1.1 | falha | skill/script | nome NyxAPI |
| 1.2 | atende | skill/script | nyx-prod |
| 1.3 | falha | skill/script | 14 ocorrências de labels ausentes/incoerentes |
| 1.4 | falha | skill/script | nyx-api x nyxapi |
| 1.5 | recomendação ausente | skill/revisão | owner ausente; runbook condicionado à existência |
| 1.6 | depende do projeto | skill/revisão | api é genérico; não afirmar violação sem convenção do componente |
| 2.1 | falha | Trivy | KSV-0011,0015,0016,0018; proporção requer consumo |
| 2.2 | falha | skill/revisão | nenhuma probe; Trivy desta rodada não apontou |
| 2.3 | falha | skill/script | 1 < 2 |
| 2.4 | falha | skill/script | estratégia explícita ausente |
| 2.5 | recomendação ausente | skill/revisão | PDB não fornecido |
| 2.6 | depende de observação | skill/revisão | default da API não prova encerramento funcional |
| 3.1 | falha | Trivy | KSV-0013 latest; digest ainda exige revisão |
| 3.2 | falha | Trivy | KSV-0001,0003,0004,0012,0014,0020,0021,0030,0104,0106,0118 |
| 3.3 | falha de padrão | skill/script | DATABASE_URL literal é marcador didático; nenhum vazamento real comprovado |
| 3.4 | falha | skill/revisão | omissão permite default habilitado |
| 3.5 | recomendação ausente | skill/revisão | serviceAccountName ausente |
| 3.6 | atende | skill/revisão | ausentes, default desabilitado |
| 3.7 | atende | skill/script | registry.metacortex.io; KSV-0125 não testa esta política específica |

KSV-0125 também reprovou o registry interno do manifesto barrado; sua lista genérica de confiança não equivale à política Metacortex. O manifesto barrado continua bloqueado. `DATABASE_URL` não é consumida pelo código kube-news consultado, que usa variáveis DB_*.

Na escrita, o primeiro Trivy encontrou 50 ocorrências (GID, seccomp e registry). Depois de definir runAsGroup=10001 e RuntimeDefault, ficaram 5 ocorrências KSV-0125 de registry público. O script encontra 16 ocorrências: 15 imagens externas (incluem initContainers) e 1 PostgreSQL de laboratório com réplica única em namespace prod. As exceções são explícitas e exclusivas do laboratório; não são aprovação Metacortex. A probe TCP de fake-shop não satisfaz endpoint funcional distinto de liveness; propor alteração da aplicação para /health e /ready ou exceção formal antes de produção.

Saídas ruins preservadas: `trivy-antes.txt`, `trivy-escrita-primeira.json`, `shop-primeira-saida-ruim.txt` e `skill-conferencia-inicial.json`. A falha de migração motivou initContainer aguardando PostgreSQL. Como o banco usa emptyDir, sua substituição no hardening exigiu reiniciar os apps para reaplicar schema; ver `reinicio-app-pos-banco.txt`. É dado efêmero de estudo, sem durabilidade/HA. Sizing tem amostra real instantânea em `consumo-instantaneo.json`, insuficiente para proporção sob carga/pico. Sem aprovação de sizing de produção.
