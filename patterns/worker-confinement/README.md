# Padrão: Worker confinado com egress-allowlist

> **Âmbito.** Engenharia de um worker autónomo isolado. Allowlists de hosts reais, chaves e
> runbooks de instalação ficam **fora** do repo. Paths e hosts fictícios (`worker.example`,
> `api.atlas-consulting.example`).

## Objectivo

Correr tarefas autónomas — potencialmente longas, potencialmente a partir de input não
totalmente confiável — **sem** dar ao worker acesso livre ao sistema nem à rede. O worker é uma
caixa com portas muito estreitas.

## Arquitectura

```
 Coordenador                                Worker confinado
     │  enfileira tarefa (assinada)                │
     ▼                                             │
 ┌────────┐   verifica assinatura     ┌────────────────────┐
 │  FILA  │ ───────────────────────► │ sandbox (FS/rede    │
 └────────┘                           │ mínimos, sem exec)  │
     ▲                                └─────────┬───────────┘
     │ resultado                                │ toda a saída
     │                                          ▼
     │                               ┌───────────────────┐
     └──────────────────────────────│ EGRESS-PROXY        │
                                     │ (allowlist fechada) │
                                     └────────────────────┘
```

## Componentes

| Componente | Função |
|---|---|
| **Fila assinada** | O coordenador enfileira tarefas com uma assinatura (ex.: HMAC com chave partilhada). O worker só executa mensagens com assinatura **válida** — impede injecção de trabalho por quem não tem a chave. |
| **Sandbox do worker** | Perfil de menor privilégio: filesystem e rede reduzidos ao mínimo da tarefa; execução de subprocessos negada. |
| **Egress-proxy** | **Toda** a rede de saída passa por um proxy com **allowlist fechada** de hosts. O resto é negado e registado. |
| **Quarentena** | Input/output suspeito é isolado numa área de quarentena, não processado. |
| **Limites de concorrência** | Cap explícito de workers simultâneos, com um **máximo duro** acima do qual não se sobe sem revisão de segurança. |

## Verificação da mensagem (conceito)

```text
# PSEUDO-CÓDIGO — a chave e o algoritmo concretos são configuração da instalação.
msg := dequeue()
if not verify_signature(msg.body, msg.sig, SHARED_KEY):   # SHARED_KEY nunca no repo
    quarantine(msg); alert("assinatura inválida — possível injecção")
else:
    run_confined(msg.body)
```

## Porquê egress-allowlist (e não denylist)

Uma **denylist** falha por **omissão** — um host novo e malicioso passa porque ninguém o
listou. Uma **allowlist** falha **seguro** — só sai o que está explicitamente permitido; tudo o
resto é negado por defeito. Descoberta dos hosts legítimos: correr a tarefa uma vez com
allowlist mínima e **observar o log de negações**, adicionando apenas os destinos genuinamente
necessários.

## Instalação e go-live

- **Backup** dos paths críticos **antes** de qualquer alteração de configuração do SO.
- Árvore de trabalho com permissões restritas; chave de assinatura com permissões `600`.
- **Provar o confinamento com um teste testemunhado** por um revisor de segurança **antes** do
  go-live (não confiar em code-review — exigir pelo menos uma execução real que demonstre que o
  egress bloqueia e a assinatura rejeita).
- Alterações a ficheiros críticos / arranque do SO são feitas **fora** do fluxo automático, com
  backup prévio.

## Princípios

1. **Assinar o trabalho** — o worker só confia em mensagens assinadas.
2. **Egress por allowlist** — negar por defeito, permitir por excepção observada.
3. **Menor privilégio** — FS e rede reduzidos ao estritamente necessário; sem subprocessos.
4. **Provar antes de confiar** — teste de confinamento testemunhado, com execução real.
5. **Segredos fora do repo** — chaves e allowlists reais nunca são versionados em público.
