# Critérios e divisão de responsabilidade

Síntese operacional do padrão, não cópia do material privado.

| Regra | Verificação |
|---|---|
| 1.1 nomes kebab-case | Script |
| 1.2 namespace cliente-dev/stg/prod | Script |
| 1.3 quatro labels em todo objeto | Script; valores coerentes com cliente/instalação |
| 1.4 seletores casam com pod | Script no conjunto de arquivos; recursos externos são não verificados |
| 1.5 owner/runbook | Instrução: dono recomendado, runbook quando existe |
| 1.6 nome de container | Instrução: nome do componente; não inferir sem projeto |
| 2.1 recursos e proporção sobre consumo | Trivy/revisão para presença; consumo real e sizing por instrução |
| 2.2 probes válidas e distintas semanticamente | Trivy/revisão para presença; código da aplicação por instrução |
| 2.3 mínimo duas réplicas em prod | Script |
| 2.4 RollingUpdate 0/1 em prod | Script |
| 2.5 PDB prod com minAvailable >= 1 | Instrução; recomendado |
| 2.6 grace period e SIGTERM | Instrução e observação da aplicação |
| 3.1 imagem imutável | Script bloqueia latest/sem tag; imutabilidade de tag por instrução |
| 3.2 securityContext | Trivy/revisão: UID 10001, non-root, sem escalation, rootfs read-only, drop ALL; conferir paths graváveis |
| 3.3 segredo não versionado | Script detecta alguns valores suspeitos; revisão complementar obrigatória, inclusive comentários/Secret |
| 3.4 token automático desabilitado | Trivy/revisão e confirmar necessidade da API |
| 3.5 service account dedicada | Instrução; recomendada |
| 3.6 hostNetwork/hostPID/privileged proibidos | Trivy/revisão |
| 3.7 registry interno | Script |

O script não é scanner completo de segredos. A cobertura real do Trivy ainda não foi medida: não há equivalência comprovada entre o catálogo do Trivy e o padrão. Até medir, a revisão humana/agente precisa cobrir explicitamente cada linha. Glossário não empacotado.
