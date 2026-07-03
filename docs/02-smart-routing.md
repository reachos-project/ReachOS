# 02 — Encaminhamento inteligente (5 rotas)

O coordenador classifica **cada** pedido numa de cinco rotas. A classificação é automática e
baseia-se na complexidade, no tipo de tarefa e nos agentes disponíveis.

## Rota 1 — Directa (sem agente)

**Quando:** perguntas sobre o estado do sistema, status de tarefas, aprovações simples,
qualquer coisa que o coordenador responde com informação que já tem.
**Acção:** resposta imediata, sem delegação.
**Exemplos:** *"Quantos agentes temos?"* · *"Qual o estado da tarefa 3?"* · *"Aprovado."*

## Rota 2 — Micro-edição (coordenador executa)

**Quando:** edições simples em ficheiros de configuração do sistema, < 5 min, sem pesquisa
nem criação de conteúdo.
**Acção:** o coordenador executa directamente com leitura + edição.
**Exemplos:** *"Corrige este typo no ficheiro de regras."* · *"Adiciona esta entrada ao roster."*

## Rota 3 — Agente-único

**Quando:** o domínio corresponde claramente a um agente existente; deliverable único e claro.
**Acção:** o coordenador delega ao agente adequado e regista a tarefa.

Cada organização mantém um **mapa de delegação** — domínio → agente. Exemplo genérico:

| Domínio do pedido | Agente |
|---|---|
| Análise de mercado, estratégia | `{{AGENT_SLUG_STRATEGY}}` |
| Redacção e edição de relatórios | `{{AGENT_SLUG_EDITOR}}` |
| Curadoria de conhecimento, memória | `{{AGENT_SLUG_KNOWLEDGE}}` |

Ver um mapa instanciado em `examples/atlas-consulting/routing-map.md`.

## Rota 4 — Pipeline (contratação)

**Quando:** o pedido exige um domínio que nenhum agente cobre.
**Acção:** pipeline de contratação (pesquisa de competências → desenho de persona → confirmação),
descrito em `docs/01-orchestration.md`.

## Rota 5 — Paralelo

**Quando:** o pedido tem várias sub-tarefas independentes, cada uma para um agente diferente.
**Acção:** decompor, lançar agentes em simultâneo, sintetizar no fim.
**Exemplo:** *"Analisa o mercado X **e** prepara material sobre o tema Y"* → dois agentes em paralelo.

## Regras de fallback

1. **Domínio ambíguo** — cabe em mais que um agente → perguntar ao utilizador para clarificar.
2. **Agente inexistente** — activar a Rota 4 (contratação).
3. **Pedido demasiado vago** — pedir o resultado desejado antes de delegar.
4. **Erro de agente** — tentar uma vez mais com instruções refinadas; se falhar, escalar ao utilizador.

## Flag "quality-sensitive"

Para deliverables visuais, para terceiros, ou de publicação, aplicar um gate de qualidade mais
exigente e sugerir revisão humana antes de finalizar (ver `docs/04-quality-gate.md`).

## Diagrama de decisão

```
Pedido
  ├─ Responde-se com info já disponível? ─────► Rota 1
  ├─ É micro-edição de config (<5 min)? ──────► Rota 2
  ├─ Domínio claro + agente existe? ────────► Rota 3
  ├─ Precisa de agente que não existe? ───────► Rota 4
  └─ Várias sub-tarefas independentes? ───────► Rota 5
```
