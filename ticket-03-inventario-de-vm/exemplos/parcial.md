# Inventário — "vm-exemplo" ("192.0.2.10")
Coletado em 2026-11-10T12:00:00Z · baseline v1

## Desvios

| Severidade | Regra | Esperado | Encontrado |
|---|---|---|---|

## Não verificado

| Regra | Motivo |
|---|---|
| chaves_ssh.emitidas_por | "cobertura parcial: arquivo inacessível" |
| ssh.login_de_root | "consulta exige privilégio não concedido" |

## Conforme

so.distribuicao · so.versao_minima · kernel.versao_minima · servicos.ativos · servicos.proibidos · swap.habilitado · portas_em_escuta.publicas_permitidas · portas_em_escuta.somente_rede_interna · ntp.sincronizado

## Inventário

```json
{
  "so": {
    "distribuicao": "ubuntu",
    "versao": "24.04"
  },
  "kernel": {
    "versao": "6.8.0-generic"
  },
  "servicos": [
    {
      "nome": "ssh.service",
      "tipo": "service",
      "estado": "active"
    },
    {
      "nome": "containerd.service",
      "tipo": "service",
      "estado": "active"
    },
    {
      "nome": "node_exporter.service",
      "tipo": "service",
      "estado": "active"
    },
    {
      "nome": "chrony.service",
      "tipo": "service",
      "estado": "active"
    }
  ],
  "swap": {
    "habilitado": false,
    "tamanho": 0,
    "unidade": "bytes"
  },
  "portas_em_escuta": [
    {
      "porta": 22,
      "bind": "0.0.0.0",
      "processo": "sshd",
      "protocolo": "tcp"
    },
    {
      "porta": 9100,
      "bind": "10.42.7.14",
      "processo": "node_exporter",
      "protocolo": "tcp"
    }
  ],
  "chaves_ssh": [
    {
      "usuario": "operador",
      "identificacao": "operador@metacortex-platform"
    }
  ],
  "quantidade_chaves_ssh": 1,
  "cobertura_chaves_ssh": "parcial",
  "ssh": null,
  "ntp": {
    "sincronizado": true,
    "mecanismo": "chrony"
  }
}
```
