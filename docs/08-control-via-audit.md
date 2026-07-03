# 08 — Controlo via auditoria

Um princípio de governança de dados que atravessa o sistema: preferir **escrita livre,
auditável e reversível** a **aprovação prévia obrigatória**. A aprovação em cada escrita cria
fricção e, na prática, leva a que se contorne ou se pare o fluxo. A auditoria mantém o controlo
sem travar o trabalho.

## O trade-off

| Abordagem | Custo | Risco residual |
|---|---|---|
| **Gating** (aprovar antes de cada escrita) | Alta fricção; interrompe o fluxo constantemente. | Baixo — mas só se as pessoas não contornarem o gate. |
| **Auditoria** (escrever livre + registar + rever) | Baixa fricção. | Contido por detecção-e-reversão dentro de latência limitada. |

A escolha depende de **onde está o risco real**. A regra prática: colocar o gate destrutivo
onde uma acção é **irreversível**, e usar auditoria onde a acção é **reversível**.

## Onde aplicar cada um

- **Gate duro (bloqueio prévio):** operações irreversíveis — apagar/reescrever configuração
  crítica, expor segredos. Aqui o custo de errar é catastrófico e o bloqueio justifica-se.
- **Auditoria (escrita livre + revisão ex-post):** a maioria das escritas de conteúdo —
  memórias, notas, registos. Uma entrada errada é sempre reversível porque a fonte-de-verdade é
  markdown e existe um histórico append-only.

## Padrão de auditoria

```
Escrita  ──►  Registo na fila de auditoria (conteúdo real, não só sumário)
                     │
                     ▼
        Cruzamento com o histórico de actividade
                     │  (heurística: anomalias — segredos, URLs, injecção)
                     ▼
        Só as anomalias são trazidas à atenção do humano
                     │
                     ▼
        Revisão on-demand + reversão trivial (SoT em markdown)
```

- A escrita continua **livre** — a fila não é um gate.
- A fila guarda o **conteúdo real** para permitir revisão fiel, não apenas um resumo.
- No arranque de sessão, mostra-se apenas a **contagem** e as **anomalias** — não um ecrã de
  revisão por sessão.
- A auditoria completa é **on-demand**. A reversibilidade total vem da fonte-de-verdade em
  markdown + histórico de actividade.

## Defence-in-depth para a própria auditoria

Cruzar duas fontes: os eventos registados no histórico **versus** os items na fila. Um evento
de escrita sem item correspondente na fila sinaliza um registo falhado — a auditoria audita-se
a si própria.

## Cuidado com dados sensíveis

Se a fila de auditoria duplica conteúdo em claro, então **nenhum conteúdo sensível** (dados
pessoais especiais, segredos, chaves de re-identificação) pode viver nas memórias auditadas —
esses dados pertencem a stores próprios, nunca a uma memória de texto livre.

## Princípio

> Controlo não é o mesmo que bloqueio. Escrita livre + auditável + reversível dá mais controlo
> real do que uma fila de aprovações que as pessoas aprendem a contornar — desde que o gate
> duro proteja o que é genuinamente irreversível.
