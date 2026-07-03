# Glossário

Termos usados de forma consistente em todo o repo.

| Termo | Definição |
|---|---|
| **Coordenador (CEO-virtual)** | Agente central que interpreta pedidos, delega e sintetiza. Não executa trabalho operacional. |
| **Agente especializado** | Persona com domínio próprio (ex.: analista, editor, curador). Recebe delegações do coordenador. |
| **Rota** | Classe de encaminhamento de um pedido. Existem 5 (ver `docs/02-smart-routing.md`). |
| **Delegação** | Transferência de uma tarefa do coordenador para um agente, registada para rastreabilidade. |
| **Memória hot / warm / cold** | Três níveis de persistência: carregado-sempre / on-demand / arquivo semântico. |
| **Fonte-de-verdade (SoT)** | O artefacto autoritativo. No modelo aqui descrito, são ficheiros markdown; índices são derivados. |
| **Índice vectorial** | Camada de retrieval semântico construída por cima da SoT; nunca a substitui. |
| **ETL incremental** | Processo que re-mineia a SoT para o índice de forma idempotente. |
| **Quality gate (QG)** | Checklist bloqueante corrido antes de entregar um deliverable. |
| **Deliverable** | Artefacto final produzido por um agente e entregue ao utilizador. |
| **Guardrail** | Controlo automático que autoriza ou bloqueia uma acção antes de esta ocorrer. |
| **Defence-in-depth** | Sobreposição de várias camadas de guardrails independentes. |
| **Tier-1 (paths críticos)** | Ficheiros de configuração/identidade cuja alteração exige protecção reforçada. |
| **Heartbeat** | Daemon periódico confinado que faz verificações e escala por custo. |
| **Egress-allowlist** | Lista fechada de destinos de rede que um worker confinado pode contactar. |
| **Controlo-via-auditoria** | Filosofia: escrita livre + registada + reversível, em vez de aprovação prévia obrigatória. |
| **Placeholder / token** | Marcador `{{TOKEN}}` a substituir por um valor concreto ao instanciar um template. |
