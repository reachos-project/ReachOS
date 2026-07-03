# 06 — Heartbeat (daemon confinado com escalada por custo)

> **Âmbito.** Descreve o **padrão** de um daemon periódico de vigilância. Os perfis de
> confinamento reais (sandbox), canais de notificação e paths ficam fora deste repo.

## Objectivo

Um processo periódico e **confinado** que faz verificações de saúde do sistema entre sessões e,
quando encontra algo, escala pela via mais barata possível — só usando um modelo de linguagem
quando estritamente necessário, e nunca agindo de forma irreversível sozinho.

## Escalada por custo (tiers)

```
Tier-0  Verificação determinista (sem LLM)
            │  encontrou algo que precisa de julgamento?
            ▼
Tier-1  Triagem com modelo local pequeno (data-only, schema fechado, fail-safe)
            │  precisa de acção/decisão humana?
            ▼
Tier-2  Enfileira para a próxima sessão + notifica
```

- **Tier-0** resolve a maioria dos casos sem qualquer modelo — é barato e determinista.
- **Tier-1** usa um modelo **local** pequeno, restrito a dados, com resposta de schema fechado
  e comportamento *fail-safe* (na dúvida, marca "requer atenção").
- **Tier-2** nunca executa acções de risco: **enfileira** o que encontrou e **notifica**. A
  decisão fica para um humano ou para a próxima sessão interactiva.

## Confinamento

O daemon corre sob um **perfil de sandbox** que restringe:

- **Filesystem:** escrita apenas em `{fila, estado, logs}`; negado a paths críticos.
- **Rede:** saída apenas para o modelo local e para o canal de notificação — mais nada.
- **Processos:** execução de subprocessos negada.
- **Base de dados:** acesso read-only.

## Segurança operacional

| Mecanismo | Função |
|---|---|
| **Kill-switch soft** | Um ficheiro-flag (`DISABLED`) faz o daemon abortar no topo do tick. |
| **Kill-switch hard** | Desregistar o serviço do gestor de arranque do SO. |
| **Circuit-breaker** | Em falha grave (excepções repetidas, rajada, schema rejeitado) o daemon desactiva-se e **não auto-recupera** — exige acknowledgement humano. |
| **Idempotência** | Claims exclusivos (criação atómica) evitam executar a mesma acção duas vezes se houver sobreposição. |
| **Scrubber de segredos** | A escrita na fila remove segredos de forma *fail-closed*. |

## Consumo lado-sessão

No arranque de uma sessão interactiva, o coordenador drena a fila: lê os registos estruturados,
move cada um para "processado" (de forma atómica), apresenta os alertas ao utilizador e
reconcilia o histórico. O daemon **não** escreve directamente no store transaccional — a
sessão interactiva é que consolida.

## Princípios

1. **O mais barato que resolve** — determinista antes de local, local antes de enfileirar.
2. **Nunca age de forma irreversível sozinho** — a acção de risco é sempre diferida a um humano.
3. **Confinado por desenho** — menos privilégio possível; rede e FS mínimos.
4. **Observável** — log append-only como fonte de verdade do daemon; ficheiro de liveness por tick.
