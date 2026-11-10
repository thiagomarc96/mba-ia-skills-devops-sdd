# Inventário SSH — especificação

Escrita antes da implementação, em 10/11/2026, após o brainstorm.

## Contrato

A CLI recebe host, usuário, caminho de chave local, baseline YAML e diretório local de saída. Python 3 deve existir no host; não será instalado. OpenSSH autentica sem senha interativa e exige chave de host já conhecida. Nenhuma chave ou stderr bruto será registrado. Comandos remotos somente consultam estado e não usam sudo.

O coletor retorna identificação, SO, kernel, serviços e sockets ativos, swap, portas/bind/processo, quantidade e identificações de chaves autorizadas, login root efetivo e NTP. Campo cuja coleta falhou é nulo e acompanhado de motivo. A cobertura de chaves depende de configuração efetiva e leitura de todos os arquivos das contas enumeradas. Fontes externas ou acesso insuficiente mantêm a regra não verificada. O comentário identifica a emissão declarada, sem comprovação criptográfica. Erros de argumentos não reproduzem os valores recebidos.

Cada regra do baseline retorna esperado, encontrado e conforme/desvio/nao_verificado. Desvios recebem a severidade declarada. Versões são comparadas numericamente; bind wildcard é público. Somente RFC1918, IPv6 ULA e loopback são internos. Falta de permissão não equivale a lista vazia.

JSON e Markdown são produzidos do mesmo objeto. Códigos: 0 conforme; 1 desvio, inclusive com itens não verificados; 2 somente itens não verificados; 3 entrada/conexão inválida. Nenhuma exceção crua deve chegar ao terminal.

## Cenários de aceite

- Dado inventário conforme, todas as regras são conformes e o retorno é 0.
- Dado kernel antigo, swap ativo ou porta pública indevida, cada regra divergente recebe a severidade do YAML.
- Dado acesso insuficiente, a regra correspondente é nao_verificado, sem impedir as demais.
- Dada falha de SSH, apresentar motivo resumido sem conteúdo da chave ou stack trace e retornar 3.
- Dadas duas coletas sem mudanças, os vereditos são iguais; o timestamp pode mudar.
- Os dois formatos concordam em contagens e decisões.
