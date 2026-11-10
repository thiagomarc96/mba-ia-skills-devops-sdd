# Curadoria

## Recorte

Mantido somente o dashboard mínimo. As decisões de stack, cliente Kubernetes, atualização, EndpointSlice e primeira fatia com duas alternativas cada foram registradas no brainstorm antes da implementação. Specs foram escritas antes do código. Não há banco, deploy da aplicação no cluster ou funcionalidade de correção.

## Refinamentos durante a implementação

- A spec descrevia endpoint pronto; o código distingue ready=true, false e ausente. Ready ausente fica desconhecido, evitando afirmar saúde sem evidência.
- Services ExternalName não possuem EndpointSlice; agora são apresentados como DNS externo.
- Nome do contexto fixado não significa snapshot imutável do kubeconfig. Essa limitação foi explicitada no design.
- Uma falha ao obter o contexto não encerra com stack trace: a tela informa o erro, e requer reinício após corrigir o ambiente.

## Uso das skills

Disparos espontâneos, chamadas manuais e acionamentos indevidos: não avaliados.
