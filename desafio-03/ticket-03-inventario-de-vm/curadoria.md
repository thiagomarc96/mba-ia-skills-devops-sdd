# Curadoria

Mantive coleta e avaliação separadas: uma consulta negada não interrompe as outras nem produz conformidade por ausência de dado. O contrato foi refinado antes do código para definir precedência dos retornos e comparação numérica de versões.

OpenSSH foi escolhido para aproveitar a autenticação existente, sem implementar protocolo. Paramiko adicionaria dependência e política própria de host keys; Ansible ampliaria o escopo e os requisitos locais. Python remoto evita parsing de saída composta por shell, mas exige Python já instalado; a ferramenta não instala nada.

O coletor executa consultas fixas, sem sudo, escritas ou comando recebido do usuário. A coleta verifica a configuração efetiva de SSH por conta enumerada e lê os arquivos AuthorizedKeysFile resolvidos, incluindo caminhos customizados. AuthorizedKeysCommand, autoridade certificadora ou configuração/arquivo inacessível tornam a cobertura parcial; nenhum comando de fonte externa é executado. A saída inclui quantidade e identificação das chaves legíveis, sem material criptográfico. O comentário representa emissão declarada, não comprovação criptográfica. A política é efetiva para as condições da conexão consultada, não para todos os blocos Match possíveis.

O enunciado deixa implícita a definição de rede interna; a especificação adotou RFC1918, IPv6 ULA e loopback. Wildcard e endereços não reconhecidos não são internos. O processo de uma porta pode não estar visível ao usuário comum e permanece nulo, sem inventar proprietário.

A execução SSH real está em [evidencias/t03](../../evidencias/t03/). Duas coletas independentes produziram 6 regras conformes, 2 desvios e 3 não verificadas, ambas com retorno 1. Swap aparece habilitado na visão do kernel compartilhado; root é permitido por chave apenas no alvo descartável. Serviços e NTP dependem de systemd, ausente como PID 1, e permanecem não verificados. Não foram criados substitutos para systemctl ou timedatectl.

Saída ruim: a primeira tentativa do laboratório retornou 3 por autenticação recusada. O arquivo público montado tinha proprietário do usuário local, incompatível com StrictModes do OpenSSH. O preparo passou a instalar somente a chave pública com proprietário root e modo 600 dentro do container. A chave privada permaneceu no diretório temporário externo; o coletor não precisou alterar sua política de autenticação.

A repetição reutilizou a chave efêmera e o mesmo alvo, mas abriu outra conexão SSH e executou novamente o Python remoto. Os instantes diferem e os vereditos coincidem. Depois o servidor foi parado: TCP recusou a conexão e a CLI retornou 3, sem relatório de conformidade. O container e os arquivos temporários foram removidos.

A CLI aceita porta e known_hosts explícitos para isolar o laboratório sem modificar a configuração SSH pessoal. A especificação, os testes e os artefatos OpenSpec foram validados antes do arquivamento. O ensaio cobre um container Linux; systemd e NTP numa VM completa permanecem fora da evidência de integração.
