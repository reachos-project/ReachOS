# Exemplo — Atlas Consulting

Uma instância **fictícia e completa** dos templates deste repo, para servir de referência.
A "Atlas Consulting" é uma empresa de consultoria inventada; o coordenador chama-se **Atlas**
e tem três agentes. Todos os nomes, pessoas, números e paths aqui são **inventados** e
existem apenas para ilustrar como os padrões se instanciam.

## Conteúdo

| Ficheiro | O que ilustra |
|---|---|
| `atlas-consulting/ORCHESTRATOR.md` | Ficheiro do coordenador instanciado a partir do template. |
| `atlas-consulting/routing-map.md` | Mapa de delegação domínio → agente. |
| `atlas-consulting/agents/market-analyst.md` | Agente de análise de mercado (persona fictícia). |
| `atlas-consulting/agents/proposal-editor.md` | Agente de redacção/edição (persona fictícia). |
| `atlas-consulting/agents/knowledge-steward.md` | Agente de curadoria de conhecimento (persona fictícia). |
| `db/schema.example.sql` | Schema conceptual do store transaccional (rastreabilidade). |

## Como usar

Lê estes ficheiros lado a lado com os `templates/` para veres cada `{{TOKEN}}` substituído por
um valor concreto. Depois cria a tua própria instância a partir dos templates — **não** copies
a Atlas Consulting como se fosse produção.
