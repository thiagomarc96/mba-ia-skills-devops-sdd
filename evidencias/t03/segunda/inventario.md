# Inventário — "inventario-ssh-local" ("127.0.0.1")
Coletado em 2026-11-18T20:19:11.018839+00:00 · baseline v1

## Desvios

| Severidade | Regra | Esperado | Encontrado |
|---|---|---|---|
| critico | swap.habilitado | false | true |
| alto | ssh.login_de_root | false | true |

## Não verificado

| Regra | Motivo |
|---|---|
| servicos.ativos | "consulta indisponível ou exige privilégio não concedido" |
| servicos.proibidos | "consulta indisponível ou exige privilégio não concedido" |
| ntp.sincronizado | "consulta indisponível ou exige privilégio não concedido" |

## Conforme

so.distribuicao · so.versao_minima · kernel.versao_minima · portas_em_escuta.publicas_permitidas · portas_em_escuta.somente_rede_interna · chaves_ssh.emitidas_por

## Inventário

```json
{
  "so": {
    "distribuicao": "ubuntu",
    "versao": "24.04"
  },
  "kernel": {
    "versao": "6.8.0-149-generic"
  },
  "servicos": null,
  "swap": {
    "habilitado": true,
    "tamanho": 2147479552,
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
      "porta": 22,
      "bind": "::",
      "processo": "sshd",
      "protocolo": "tcp"
    }
  ],
  "chaves_ssh": [
    {
      "usuario": "root",
      "identificacao": "estudo@metacortex-platform"
    }
  ],
  "ssh": {
    "login_de_root": true,
    "politica": "without-password",
    "escopo": "conexao_atual"
  },
  "ntp": null,
  "quantidade_chaves_ssh": 1,
  "cobertura_chaves_ssh": "completa_para_contas_enumeradas_e_conexao_atual"
}
```
