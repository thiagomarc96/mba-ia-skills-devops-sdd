# Inventário — "vm-exemplo" ("192.0.2.10")
Coletado em 2026-11-10T12:01:00Z · baseline v1

## Desvios

| Severidade | Regra | Esperado | Encontrado |
|---|---|---|---|
| medio | kernel.versao_minima | "6.5" | "5.15.0-118-generic" |
| alto | servicos.ativos | ["ssh", "containerd", "node_exporter", "chrony"] | ["containerd.service", "node_exporter.service", "ssh.service"] |
| critico | swap.habilitado | false | true |
| critico | portas_em_escuta.publicas_permitidas | [22] | [{"porta": 22, "bind": "0.0.0.0", "processo": "sshd", "protocolo": "tcp"}, {"porta": 9100, "bind": "0.0.0.0", "processo": "node_exporter", "protocolo": "tcp"}] |
| critico | portas_em_escuta.somente_rede_interna | [9100] | [{"porta": 22, "bind": "0.0.0.0", "processo": "sshd", "protocolo": "tcp"}, {"porta": 9100, "bind": "0.0.0.0", "processo": "node_exporter", "protocolo": "tcp"}] |
| medio | ntp.sincronizado | true | false |

## Não verificado

| Regra | Motivo |
|---|---|

## Conforme

so.distribuicao · so.versao_minima · servicos.proibidos · chaves_ssh.emitidas_por · ssh.login_de_root

## Inventário

```json
{
  "so": {
    "distribuicao": "ubuntu",
    "versao": "24.04"
  },
  "kernel": {
    "versao": "5.15.0-118-generic"
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
    }
  ],
  "swap": {
    "habilitado": true,
    "tamanho": 4294967296,
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
      "bind": "0.0.0.0",
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
  "cobertura_chaves_ssh": "completa_para_contas_enumeradas_e_conexao_atual",
  "ssh": {
    "login_de_root": false,
    "politica": "no",
    "escopo": "conexao_atual"
  },
  "ntp": {
    "sincronizado": false,
    "mecanismo": "não identificado"
  }
}
```
