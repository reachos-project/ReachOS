# ReaCH — Reference Architecture for Coordinated Hives

**ReaCH** (*Reference Architecture for Coordinated Hives*) é uma **arquitectura de referência**
para orquestrar uma equipa de agentes de IA especializados
sob um coordenador central ("CEO-virtual"). Documenta os padrões que uma organização pode
estudar e reutilizar: encaminhamento de pedidos, controlo de qualidade, memória persistente,
guardrails de segurança e automação confinada.

> **Aviso.** Isto é uma *reference architecture*, não software pronto a correr. Todos os
> nomes, empresas, agentes, paths e números são **fictícios e ilustrativos**. Adapta os
> templates ao teu contexto antes de usar.

---

## O que é

O padrão central é simples: um **coordenador** interpreta o pedido do utilizador, **delega**
para o agente especializado adequado, **sintetiza** o resultado e entrega. O coordenador nunca
faz o trabalho operacional — orquestra.

```
Utilizador → Coordenador → Agente especializado → Coordenador → Utilizador
```

Sobre este esqueleto assentam cinco famílias de padrões:

1. **Orquestração** — regras de governança do coordenador (delegação, cadeia de comando, rastreabilidade).
2. **Encaminhamento inteligente** — classificar cada pedido numa de 5 rotas.
3. **Memória 3-tier** — hot / warm / cold, com markdown como fonte-de-verdade e índice vectorial derivado.
4. **Quality gate** — checklist bloqueante antes de qualquer entrega.
5. **Guardrails + automação confinada** — defence-in-depth, daemon de heartbeat, workers com egress-allowlist.

---

## Mapa mental

- **Rotas** (`docs/02-smart-routing.md`): Directa · Micro-edição · Agente-único · Pipeline · Paralelo.
- **Memória** (`docs/03-memory-3tier.md`): hot (cada sessão) · warm (on-demand) · cold (arquivo semântico).
- **Guardrails** (`docs/05-guardrails.md`): 3 camadas — matcher → inspecção de conteúdo → backups.

---

## Estrutura do repo

| Pasta | Conteúdo |
|---|---|
| `docs/` | O "porquê" e o "como" de cada padrão, em prosa. |
| `templates/` | Esqueletos parametrizáveis com placeholders `{{TOKEN}}`. |
| `examples/` | Uma instância fictícia completa ("Atlas Consulting"), schema de exemplo e esqueletos de guardrails. |
| `patterns/` | Engenharia profunda dos padrões de segurança (defence-in-depth, heartbeat, worker confinado, tripwire/baseline, watchdog recíproco). |
| `NOTICE` | Atribuição de linhagem aos upstreams (ver Acknowledgments abaixo). |

## Como usar os templates

Cada template usa tokens `{{MAIÚSCULAS_ENTRE_CHAVETAS}}`. Substitui pelos teus valores:

| Token | Significado | Exemplo |
|---|---|---|
| `{{PROJECT_ROOT}}` | Raiz do projecto | `/opt/atlas/assistant` |
| `{{ORCHESTRATOR_NAME}}` | Nome do coordenador | `Atlas` |
| `{{OWNER_HANDLE}}` | Utilizador humano | `owner` |
| `{{AGENT_SLUG}}` | Slug de um agente | `market-analyst` |
| `{{NOTIFY_CHANNEL}}` | Canal de alertas | `<your-notify-url>` |
| `{{DB_PATH}}` | Base de dados de estado | `./state/assistant.db` |

## O que este repo NÃO contém

Por desenho, foram **excluídos**: quaisquer segredos ou credenciais, personas internas reais,
paths pessoais ou hostnames, a topologia real dos controlos de segurança (regras de detecção,
baselines), e dados de utilizadores. O repo transmite **padrões**, não configurações vivas.

## Acknowledgments / Linhagem

Esta arquitectura não nasceu do nada — descende, com crédito e gratidão, de dois projectos
upstream. É uma reescrita **clean-room** (os padrões re-expressos a partir do conceito, com
placeholders genéricos e exemplos fictícios), não uma cópia de nenhum deles.

- **[freskhu/genesis](https://github.com/freskhu/genesis)** (Apache-2.0) — a **estrutura
  funcional** deste projecto descende do `genesis`: o modelo de coordenador CEO-virtual, a
  delegação para agentes especializados, o smart routing, o quality gate, a organização de
  skills/hooks e as convenções de schema do store de rastreabilidade. O autor partilhou a
  estrutura com a nossa equipa de forma privada, antes da publicação do repositório. Onde
  reproduzimos nomes ou nomenclatura de schema do upstream, é **consciente e atribuído**.

- **[MemPalace/mempalace](https://github.com/MemPalace/mempalace)** (MIT) — o **sistema de
  memória 3-tier** e a sua taxonomia (o "palácio" semântico e o vocabulário de wings / rooms /
  halls / drawers, mineração e travessia, o diário, e o grafo de conhecimento bitemporal)
  herdam conceitos do `mempalace`, que foi o motor original da nossa camada de memória antes de
  um sucessor interno. MIT é compatível com Apache-2.0.

Detalhe formal da atribuição no ficheiro [`NOTICE`](NOTICE). Ambas as licenças são permissivas e
mutuamente compatíveis; o crédito aqui é dado de forma visível e generosa, por obrigação
(Apache-2.0) e por reconhecimento.

## Licenças

Este repositório usa dupla licença:

- **Código, templates e esqueletos** (`templates/`, `examples/`):
  [Apache License 2.0](LICENSE)
- **Documentação** (`docs/`, `patterns/`, `README.md`, `GLOSSARY.md`, `CONTRIBUTING.md`):
  [CC-BY-4.0](LICENSE-docs)

O ficheiro [`NOTICE`](NOTICE) identifica os upstreams que deram origem a esta arquitectura e
declara a natureza clean-room deste repositório.
