# Padrão: Heartbeat — daemon confinado com escalada por custo

> **Âmbito.** Engenharia de um daemon periódico de vigilância entre sessões. Os perfis de
> sandbox reais, canais de notificação e paths ficam **fora** do repo. Paths fictícios:
> `/opt/atlas/assistant/{queue,state,logs}`.

## Objectivo

Um processo periódico e **confinado** que corre entre sessões interactivas, faz verificações de
saúde, e — quando encontra algo — escala pela via **mais barata** que resolve, usando um modelo
de linguagem só quando é mesmo preciso, e **nunca** agindo de forma irreversível sozinho.

## Escalada por custo

```
Tier-0  Verificação determinista (sem modelo)
            │ precisa de julgamento?
            ▼
Tier-1  Triagem com modelo LOCAL pequeno (data-only, schema fechado, fail-safe)
            │ precisa de decisão humana / acção de risco?
            ▼
Tier-2  Enfileira + notifica — nunca executa a acção de risco
```

- **Tier-0** resolve a maioria (espaço em disco, fila presa, certificado a expirar, ficheiros
  stale) sem qualquer modelo. Barato e determinista.
- **Tier-1** usa um modelo **local** pequeno, restrito a dados, com **resposta de schema
  fechado** e comportamento *fail-safe* (na dúvida marca "requer atenção"). Não chama a rede
  para fora nem executa comandos.
- **Tier-2** **enfileira** o achado e **notifica**. A decisão fica para a próxima sessão
  interactiva ou para um humano.

## Idempotência sob sobreposição

Se duas sessões (ou dois ticks) coincidirem, a mesma acção não pode correr duas vezes. O padrão
é um **claim exclusivo atómico**:

```text
# PSEUDO-CÓDIGO
claim := "/opt/atlas/assistant/state/tick.claim"
if not atomic_create_exclusive(claim):   # O_CREAT|O_EXCL — falha se já existir
    exit(0)                              # outro tick já está a tratar; sair limpo
try:
    do_tick()
finally:
    release(claim)
```

A criação exclusiva é a primitiva de exclusão mútua: quem cria o ficheiro ganha o tick; os
outros saem sem fazer nada.

## Segurança operacional

| Mecanismo | Função |
|---|---|
| **Kill-switch soft** | Um ficheiro-flag faz o daemon abortar no topo do tick. Reversível sem privilégios. |
| **Kill-switch hard** | Desregistar o serviço do gestor de arranque do SO. |
| **Circuit-breaker** | Perante falha grave (excepções repetidas, rajada, schema rejeitado pelo Tier-1) o daemon **desactiva-se e não auto-recupera** — exige acknowledgement humano explícito. Auto-recuperar depois de uma falha grave é como um sistema entra em loop de dano. |
| **Scrubber de segredos (fail-closed)** | A escrita na fila remove segredos; se o scrubber falhar, **não escreve** (fail-closed), em vez de escrever em claro. |
| **Ficheiro de liveness** | Cada tick actualiza um ficheiro de liveness — a base para o watchdog recíproco (ver `../reciprocal-watchdog/`). |

## Confinamento

O daemon corre sob um **perfil de sandbox** de menor privilégio:

- **Filesystem:** escrita apenas em `{fila, estado, logs}`; negado a paths críticos.
- **Rede:** saída apenas para o modelo local e para o canal de notificação — mais nada.
- **Processos:** execução de subprocessos negada.
- **Base de dados:** read-only.

> O bloco de perfil de sandbox real (as regras de deny/allow concretas) **não** faz parte deste
> repo — é topologia do sistema de confiança. Só o *conceito* de confinamento sai.

## Consumo lado-sessão

No arranque de uma sessão interactiva, o coordenador **drena a fila**: lê os registos
estruturados, move cada um para "processado" de forma **atómica**, apresenta os alertas ao
utilizador e reconcilia o histórico. O daemon **não** escreve no store transaccional — a sessão
interactiva é que consolida. Assim o daemon nunca precisa de privilégio de escrita sobre o
estado autoritativo.

## Princípios

1. **O mais barato que resolve** — determinista → local → enfileirar.
2. **Nunca age de forma irreversível sozinho.**
3. **Confinado por desenho** — FS e rede mínimos; sem subprocessos.
4. **Falha grave desactiva; não auto-recupera.**
5. **Observável** — log append-only + ficheiro de liveness por tick.
