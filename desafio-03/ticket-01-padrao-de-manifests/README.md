# Padrão de manifests — T01

A skill [manifests-metacortex](skill/SKILL.md) foi executada nos modos escrita e conferência em 18/11/2026. O fluxo começou com `trivy config manifests/`, antes de gerar os novos arquivos. A [cobertura medida e curadoria](../../evidencias/t01/cobertura.md) inclui achados, divisão de controles e saídas ruins.

```sh
python3 -m pip install -r requirements.txt
trivy config manifests/
python3 gerar_laboratorio.py
python3 skill/scripts/conferir.py manifests/*.yaml
python3 skill/scripts/conferir.py exemplos/manifesto-barrado.yaml
trivy config --skip-version-check --format json manifests/
python3 gerar_exemplos.py
python3 -m unittest discover -s tests -v
```

O verificador retorna 0 sem achados no seu recorte, 1 com achados e 2 para entrada inválida. Ele nunca aplica recursos nem executa o Trivy automaticamente. A aplicação do laboratório foi uma etapa externa à skill, autorizada separadamente.

Na escrita foram gerados manifests para nyx-dev, orion-dev, nyx-prod, orion-stg e nyx-stg. Os dois projetos ficaram Running/Ready, com banco em cada namespace: [nyx](../../evidencias/t01/kubectl-get-all-nyx-dev.txt) e [orion](../../evidencias/t01/kubectl-get-all-orion-dev.txt). O gerador é portátil e produz somente YAML; o Secret é criado pelo preparo do laboratório em memória, via stdin, com valor aleatório fora do Git.

Fontes consultadas: [kube-news aab9356](https://github.com/KubeDev/kube-news/tree/aab93563069d184c66dd1f0359bd131ffbe34433) e [fake-shop a3fa74f](https://github.com/KubeDev/fake-shop/tree/a3fa74fcadea2f163dd785313b119d4c8e03ecea). Portas, variáveis, migração e encerramento foram lidos no código. Os hashes dos arquivos presentes nas imagens estão em [imagens-codigo-hashes.txt](../../evidencias/t01/imagens-codigo-hashes.txt). `server.js` da imagem tem hash diferente do checkout; `system-life.js` e `models/post.js` coincidem. As rotas e variáveis usadas foram conferidas nesses arquivos e na execução real. `index.py` e `entrypoint.sh` de fake-shop coincidem com a fonte.

- kube-news: porta 8080; `/health` e `/ready` existem, mas não validam banco. Usa DB_HOST, DB_DATABASE, DB_USERNAME, DB_PASSWORD e DB_PORT; `DATABASE_URL` do manifesto barrado não é consumida.
- fake-shop: porta 5000; `/` consulta produtos; não oferece `/health`. O entrypoint migra antes de iniciar gunicorn. `/tmp` é gravável; o rootfs e o código ficam em leitura. A liveness TCP é uma exceção explícita de laboratório, pendente de endpoint funcional distinto antes de produção.
- Todas as imagens dos apps são públicas e fixadas por digest; PostgreSQL usa a versão 16.6-alpine. Execução confirmou UID/GID 10001, rootfs de leitura, capabilities removidas e RuntimeDefault nos devs finais.

Na conferência, o manifesto original foi preservado e bloqueado: [saída real](../../evidencias/t01/skill-conferencia.json), [revisão por regra](../../evidencias/t01/cobertura.md). O marcador `VALOR_DE_EXEMPLO` não é uma credencial real. O Trivy identificou 18 ocorrências/17 IDs; a versão final do script tem 19 ocorrências/6 regras, removendo o controle duplicado de latest. Em 14 famílias com achado, Trivy cobre 3 (21,43%) e somente skill cobre 11 (78,57%).

Os manifests de laboratório continuam com 16 achados do script (registry público e PostgreSQL com uma réplica em prod) e 5 KSV-0125 do Trivy. Não estão aprovados como conformes para produção. PDB, owner/runbook, HA, probes funcionais distintas no fake-shop e dimensionamento sob carga requerem decisão adicional. A amostra instantânea de consumo não representa pico. O banco usa emptyDir: substituir seu pod perde o conteúdo de estudo e exige reaplicar schema; isso foi observado e registrado.

A tag fixa PostgreSQL 16.6-alpine identifica a versão escolhida, mas não comprova política de imutabilidade do registry; um digest deve ser adotado para aprovação integral da regra 3.1 do banco e do initContainer.
