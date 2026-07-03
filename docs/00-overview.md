# 00 — Visão geral

## O problema

Uma única sessão de assistente generalista degrada-se quando tenta ser tudo ao mesmo tempo:
o contexto satura, o tom oscila, e não há separação de responsabilidades. A resposta é
**especialização com coordenação** — muitos agentes focados, um coordenador que os orquestra.

## O modelo

```
                    ┌─────────────────┐
   Utilizador  ───► │   COORDENADOR   │ ───► Utilizador
                    │  (CEO-virtual)  │
                    └───────┬─────────┘
                            │ delega
              ┌─────────────┬─────────────┐
              ▼             ▼             ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ Agente A │  │ Agente B │  │ Agente C │
        │ (domínio)│  │ (domínio)│  │ (domínio)│
        └──────────┘  └──────────┘  └──────────┘
```

O coordenador:
- **Interpreta** o pedido e classifica-o numa rota (`docs/02`).
- **Delega** para o agente adequado (ou vários, em paralelo).
- **Sintetiza** os resultados numa resposta coerente.
- **Nunca** faz o trabalho operacional — a única excepção são micro-edições de configuração.

Cada agente:
- Tem uma **persona** (identidade, expertise, estilo, constraints) definida num ficheiro próprio.
- Opera só no seu **workspace** designado.
- Devolve o resultado ao coordenador — **nunca** comunica directamente com o utilizador.

## Os cinco pilares

| Pilar | Documento | Ideia central |
|---|---|---|
| Orquestração | `01-orchestration.md` | Regras de governança do coordenador. |
| Encaminhamento | `02-smart-routing.md` | 5 rotas para classificar qualquer pedido. |
| Memória | `03-memory-3tier.md` | Persistência em 3 níveis, markdown como SoT. |
| Quality gate | `04-quality-gate.md` | Checklist bloqueante antes de entregar. |
| Segurança | `05-guardrails.md` · `06-heartbeat.md` · `07-worker-confinement.md` | Defence-in-depth + automação confinada. |
| Governança de dados | `08-control-via-audit.md` | Escrita livre, auditável e reversível. |

## Princípios transversais

1. **Rastreabilidade.** Toda a tarefa, delegação e entrega é registada. O histórico é consultável.
2. **Separação de responsabilidades.** Um agente = um domínio. O coordenador não invade domínios.
3. **Fonte-de-verdade explícita.** Ficheiros humanamente legíveis são autoritativos; índices são derivados.
4. **Fail-safe.** Na dúvida, os controlos bloqueiam (over-block) em vez de deixar passar.
5. **Reversibilidade.** Preferir escrita livre + auditoria a aprovação prévia que trava o fluxo.

## Como ler este repo

Começa por `01` e `02` (o núcleo da orquestração), depois `03` (memória) e `04` (qualidade).
Os documentos `05`–`07` descrevem a postura de segurança em **conceito** — os esqueletos de
implementação ficam deliberadamente fora deste repo. Instancia os `templates/` com a ajuda do
exemplo em `examples/atlas-consulting/`.
