# Padrão de manifests

Skill em `skill/SKILL.md`, verificador em `skill/scripts/conferir.py` e critérios em `skill/references/criterios.md`.

## Uso

```sh
python -m pip install -r requirements.txt
python skill/scripts/conferir.py manifests/nyx-api.yaml
trivy config manifests/
```

O script verifica somente o recorte mecânico descrito nos critérios. Saída 0 significa ausência de achados nesse recorte, não conformidade integral; 1 indica achados; 2 entrada inválida. Não acessa cluster nem executa Trivy automaticamente.

## Origem e curadoria

Origem: análise do padrão e do código do kube-news com Codex. O fluxo operacional ainda não foi executado.

O corpo contém gatilhos, limites e sequência. Regras detalhadas ficam em referência consultada sob demanda. O script concentra identidade, namespace, labels, seletores, política de produção, registry e referências de segredos. O glossário Kubernetes não foi empacotado: não é procedimento operacional. Regras gerais de segurança/resiliência são conferidas com Trivy e revisão explícita; não se afirma qual cobertura o Trivy tem sem executá-lo.

Permissões: leitura dos arquivos do projeto e execução local do verificador/Trivy; no modo escrita, criar arquivos de manifests no workspace autorizado. Sem apply, acesso a Secret, cluster ou produção. A skill não exige rede para conferir YAML já disponível.

## Projeto escolhido

Fonte: [kube-news, commit aab9356](https://github.com/KubeDev/kube-news/tree/aab93563069d184c66dd1f0359bd131ffbe34433).

- `src/server.js`: porta 8080; inicia sincronização de schema.
- `src/system-life.js`: `/health` e `/ready` existem, mas não testam banco. Readiness não prova disponibilidade funcional de PostgreSQL.
- `src/models/post.js`: variáveis `DB_HOST`, `DB_DATABASE`, `DB_USERNAME`, `DB_PASSWORD`, `DB_PORT`. O manifesto barrado usa `DATABASE_URL`, que esse código não consome.

`manifests/nyx-api.yaml` pressupõe namespace `nyx-prod`, PostgreSQL provisionado e Secret `nyx-db` com chaves host, database, username e password. Confirmar a imagem interna e sua imutabilidade, compatibilidade com UID 10001/rootfs somente leitura e sizing conforme consumo. Recursos iniciais: 100m/128Mi de requests e 500m/256Mi de limits.

## Conferência estática do manifesto barrado

Leitura do enunciado, não saída de execução da skill:

- `NyxAPI` viola nomenclatura; quatro labels obrigatórias ausentes.
- Service seleciona `app: nyx-api`, mas o pod usa `app: nyxapi`.
- Produção com uma réplica, sem estratégia explícita exigida e sem PDB recomendado.
- Requests/limits, probes e securityContext exigidos ausentes.
- Imagem `latest`; credencial em texto puro; token de service account não desabilitado.
- `DATABASE_URL` não corresponde às variáveis lidas pelo código consultado.
- Namespace `nyx-prod` e registry interno atendem ao formato. Dono, runbook e service account dedicada não foram informados.

Execuções em cluster e Trivy não realizadas.
