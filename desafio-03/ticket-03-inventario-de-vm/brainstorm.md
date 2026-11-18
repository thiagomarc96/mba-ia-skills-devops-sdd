# Inventário de VM — brainstorm

Registro anterior à implementação, em 10/11/2026.

## Menor entrega que atende

CLI executada na estação do operador. Recebe endereço, usuário, caminho da chave privada e baseline. Acessa um host Linux por SSH, sem instalar agente nem modificar o host. Produz JSON e Markdown a partir do mesmo resultado. Não incluir UI, histórico ou remediação.

## Decisões propostas

- Python com OpenSSH como subprocesso: simples para um time de infraestrutura, usa a autenticação já existente e mantém poucas dependências. Paramiko adicionaria uma implementação SSH e uma dependência; Ansible ampliaria a ferramenta além da coleta exigida.
- Coleta por comandos de leitura, com timeout e limites de saída. Privilégio ausente torna o campo indisponível; não solicitar senha nem tentar elevar privilégio automaticamente.
- Comparação do baseline separada da coleta. Ausência de evidência não equivale a conformidade. Coletor e avaliador devem distinguir conjunto vazio de coleta negada.
- Chave recebida apenas por caminho local. Não imprimir seu conteúdo, argumento completo ou stderr cru. Não desativar a verificação da chave do host SSH.
- Código de saída proposto: 0 conforme; 1 algum desvio; 2 coleta parcial sem desvio; 3 falha de conexão/entrada. Desvio tem precedência sobre coleta parcial, e os dois continuam visíveis no relatório.

## Comportamento a especificar

Identificação e instante UTC; distribuição/versão; kernel; unidades ativas com distinção service/socket; swap e tamanho; portas com bind e processo; quantidade/identificação de chaves autorizadas; política efetiva de login root; sincronização NTP e mecanismo. Uma decisão por regra do baseline com esperado, encontrado e veredito; severidade somente nos desvios.

O acesso de um usuário comum não permite afirmar que todas as chaves do host foram auditadas. Se não for possível coletar o escopo completo, registrar nao_verificado. Identificação em comentário de chave não comprova criptograficamente emissão: explicitar o critério aceito no laboratório. Para portas internas, considerar IPv4/IPv6 e não classificar wildcard como interno. Falta de visibilidade do processo deve aparecer como limitação.

## Aceite a transformar em cenários

1. Host conforme, sem desvio.
2. Host divergente com severidade por regra.
3. Regra inacessível como nao_verificado.
4. Host inacessível/chave recusada com erro útil, sem segredo e sem stack trace.
5. Duas execuções no mesmo host sem mudança, com vereditos iguais; somente o instante pode variar em host estável.
6. JSON e Markdown refletem exatamente o mesmo dado.

## Sequência

Converter as decisões em specs e uma mudança OpenSpec antes de escrever código; depois validar os cenários de aceite.
