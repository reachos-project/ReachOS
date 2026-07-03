# Atlas Consulting — Mapa de delegação

<!-- Instância fictícia. Domínio → agente, com exemplos de pedidos. -->

| Domínio do pedido | Agente | Slug |
|---|---|---|
| Dimensionamento de mercado, concorrência, tendências | Analista de Mercado | `market-analyst` |
| Documentos para clientes, propostas, relatórios, edição | Editor de Documentos | `proposal-editor` |
| Curadoria de conhecimento, memória, auditoria de freshness | Curador de Conhecimento | `knowledge-steward` |

## Exemplos de encaminhamento

| Pedido | Rota | Destino |
|---|---|---|
| *"Quantas tarefas abertas há?"* | 1 — Directa | Atlas responde |
| *"Corrige o nome do cliente no ficheiro de regras."* | 2 — Micro-edição | Atlas executa |
| *"Dimensiona o mercado de logística ibérica."* | 3 — Agente-único | `market-analyst` |
| *"Edita esta proposta para o cliente."* | 3 — Agente-único | `proposal-editor` |
| *"Dimensiona o mercado X **e** edita a proposta Y."* | 5 — Paralelo | `market-analyst` + `proposal-editor` |
| *"Precisamos de alguém para modelação financeira."* | 4 — Pipeline | Contratação de novo agente |

## Regras de fallback

1. Domínio ambíguo → perguntar ao utilizador.
2. Agente inexistente → Rota 4.
3. Pedido vago → pedir o resultado desejado.
4. Erro de agente → repetir com instruções refinadas; se falhar, escalar.
