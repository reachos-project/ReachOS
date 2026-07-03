# 01 — Orquestração

O coordenador governa-se por um pequeno conjunto de regras de ouro. São propositadamente
poucas e estáveis — a complexidade vive nos agentes, não no coordenador.

## Regra 1 — Delegação total

O coordenador **nunca** faz trabalho operacional directamente. Delega sempre para o agente
especializado adequado. Única excepção: micro-tarefas de configuração (< 5 min) em ficheiros
do próprio sistema.

> *Porquê:* concentrar execução no coordenador re-satura o contexto e apaga a especialização.

## Regra 2 — Cadeia de comando

O fluxo de qualquer pedido é sempre o mesmo:

```
Utilizador → Coordenador → Agente → Coordenador → Utilizador
```

Nenhum agente comunica directamente com o utilizador. Toda a comunicação passa pelo coordenador,
que faz a síntese final. Isto garante um único ponto de coerência e de controlo de qualidade.

## Regra 3 — Rastreabilidade

Toda a tarefa, delegação e deliverable é registada num store transaccional (ver
`examples/db/schema.example.sql`). O utilizador pode consultar o histórico a qualquer momento.
O registo mínimo por tarefa:

1. Criar a tarefa ao receber o pedido.
2. Registar cada delegação entre agentes.
3. Actualizar a tarefa ao concluir (estado + resumo do resultado).
4. Registar o deliverable quando um ficheiro é entregue.

## Regra 4 — Quality gate

Antes de entregar qualquer output, o coordenador corre um checklist de qualidade
(`docs/04-quality-gate.md`). Se o deliverable não passa, não sai. O resultado do gate é
registado para permitir métricas longitudinais de qualidade.

## Regra 5 — Privacidade e segurança

Respeitar a privacidade do utilizador. Nunca expor dados sensíveis. Os agentes só escrevem nos
seus workspaces designados; qualquer escrita fora disso é bloqueada por guardrail (`docs/05`).

## Regra 6 — Validação pré-alteração (para config crítica)

Antes de aplicar qualquer alteração a ficheiros de configuração críticos ("Tier-1"), correr um
*dry-run* que valida as assunções da alteração:

- Os items a **remover** existem mesmo no estado actual?
- Os items a **adicionar** já lá estão (alteração redundante)?
- A estrutura assumida ainda se verifica?

Se há divergência entre o estado assumido e o real, **parar** e re-avaliar antes de aplicar.
Isto evita regressões causadas por alterações desenhadas contra um estado obsoleto.

## Regra 7 — Backup antes de operação destrutiva

Antes de correr qualquer processo capaz de apagar/mover/truncar ficheiros de configuração
críticos, criar **backup verificável** (arquivo + manifesto de hashes) e confirmar a integridade
do backup **antes** de prosseguir. Ler e inspeccionar semanticamente qualquer script que toque
esses paths — validação de sintaxe não chega.

> *Porquê:* um comando destrutivo embutido num script não passa pela camada de autorização que
> só intercepta no limiar coordenador→ferramenta. Sem backup, a perda é irreversível.

## Contratação de novos agentes (pipeline)

Quando é preciso um domínio que nenhum agente cobre:

1. **Pesquisa de competências** — um agente investiga o perfil ideal e produz um relatório.
2. **Desenho da persona** — outro agente desenha a identidade e escreve o ficheiro do agente.
3. **Confirmação** — o coordenador regista o novo agente e actualiza o roster.

Ver o template em `templates/agents/agent.template.md`.
