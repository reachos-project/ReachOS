# 04 — Quality gate

Antes de qualquer deliverable sair para o utilizador ou terceiros, corre um checklist
bloqueante. A ideia é simples: **se não passa, não sai**. O resultado é registado para
permitir métricas de qualidade ao longo do tempo.

## Quando correr

- **Obrigatório** antes de qualquer entrega para o utilizador, stakeholders ou destinos externos.
- **Obrigatório** para deliverables *quality-sensitive* (visuais, para terceiros, de publicação).
- **Opcional** para drafts internos e notas privadas.

## Checklist estrutural (bloqueante)

Cada item que falha bloqueia a entrega:

1. **Naming** — segue a convenção de nomes e está no local certo; nome único (não colide).
2. **Metadados** — frontmatter/propriedades preenchidos (título, data, autor).
3. **Sem duplicação adjacente** — nenhum parágrafo é idêntico ao seguinte (artefacto comum de conversão).
4. **Fluxo de imagens** — cada imagem tem legenda única e posição coerente (não logo após um heading vazio).
5. **Convenções de anotação** — anotações do coordenador estão marcadas e com fonte; nunca confundíveis com a voz do autor.
6. **Linguagem e estilo** — idioma consistente, ortografia correcta, tom adequado, tipografia esperada.
7. **Referências cruzadas** — links internos apontam para ficheiros que existem; caminhos funcionam.
8. **Tabelas e caixas** — bem formatadas; número de colunas consistente; listas sem items órfãos.
9. **Sem marcadores de LLM** — sem separadores/frases formulaicas típicas de geração automática.

## Checklist de conteúdo (warning, não bloqueante)

10. **Densidade** — nenhuma secção vazia ou só com *TODO*; sem placeholders por resolver.
11. **Actionability** — acções de follow-up têm dono e prazo; perguntas abertas estão marcadas.
12. **Coerência de estilo** — alinhado com o guia de estilo aplicável ao registo (formal, técnico, etc.).

## Score e decisão

```
Score estrutural: X / 9
Score conteúdo:   Y / 3
Score total:      Z / 12

Recomendação:
  SHIP        se Z ≥ 10/12  e  zero bloqueantes
  FIX FIRST   se há bloqueantes
  REVIEW      se há warnings mas nenhum bloqueante
```

- Regra base: **mínimo 10/12 e zero bloqueantes**.
- Para deliverables *quality-sensitive*: **mínimo 11/12** + revisão visual humana.
- Máximo 2 rondas de correcção antes de escalar ao utilizador.

## Registo e métricas

Após correr o checklist, registar o resultado (score estrutural, score de conteúdo, número de
iterações, tags). Isto alimenta um KPI de qualidade. Um sinal útil: **divergência** entre o
score estrutural (12/12) e a satisfação subjectiva do utilizador (ex.: 6/10) indica uma falha
sistémica que o checklist não capta — gatilho para refinar o próprio gate.

## Verificação linguística (exemplo)

Um gate de idioma pode ser automatizado. Exemplo para um idioma com acentuação obrigatória:
contar caracteres acentuados num documento longo; um resultado próximo de zero num texto que
devia tê-los é um *fail* linguístico. Adapta ao teu idioma-alvo.
