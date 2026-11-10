# Curadoria

Mantive coleta e avaliação separadas: uma consulta negada não interrompe as outras nem produz conformidade por ausência de dado. O contrato foi refinado antes do código para definir precedência dos retornos e comparação numérica de versões.

OpenSSH foi escolhido para aproveitar a autenticação existente, sem implementar protocolo. Paramiko adicionaria dependência e política própria de host keys; Ansible ampliaria o escopo e os requisitos locais. Python remoto evita parsing de saída composta por shell, mas exige Python já instalado; a ferramenta não instala nada.

O coletor executa consultas fixas, sem sudo, writes ou comando recebido do usuário. A coleta verifica a configuração efetiva de SSH por conta enumerada e lê os arquivos AuthorizedKeysFile resolvidos, incluindo caminhos customizados. AuthorizedKeysCommand, autoridade certificadora ou configuração/arquivo inacessível tornam a cobertura parcial; nenhum comando de fonte externa é executado. A saída inclui quantidade e identificação das chaves legíveis, sem material criptográfico. O comentário representa emissão declarada, não comprovação criptográfica. A política é efetiva para as condições da conexão consultada, não para todos os blocos Match possíveis.

O enunciado deixa implícita a definição de rede interna; a especificação adotou RFC1918, IPv6 ULA e loopback. Wildcard e endereços não reconhecidos não são internos. O processo de uma porta pode não estar visível ao usuário comum e permanece nulo, sem inventar proprietário.

Não houve divergência observada em execução remota nem correção de especificação decorrente desse teste. O arquivamento da mudança permanece pendente.
