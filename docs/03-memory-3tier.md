# 03 — Memória 3-tier

A equipa partilha uma memória persistente em três níveis. O princípio orientador é
**markdown-as-source-of-truth**: os ficheiros markdown são autoritativos; qualquer índice
(vectorial, base de dados) é uma camada **derivada** que nunca os substitui.

## Os três níveis

| Nível | Descrição | Acesso |
|---|---|---|
| **Hot** | Perfil do utilizador, preferências, regras. Carregado em **cada** sessão. | Ficheiro markdown lido no arranque. |
| **Warm** | Decisões de projecto, padrões aprendidos, histórico de contratações. | Markdown, consultável on-demand por leitura, grep ou pesquisa semântica. |
| **Cold** | Arquivo histórico semântico + grafo de conhecimento temporal. | Via ferramentas de pesquisa/grafo do índice derivado. |

## Fonte-de-verdade e índice derivado

```
   Utilizador edita markdown
            │
            ▼
   ETL incremental re-mineia   (idempotente, por hash de conteúdo)
            │
            ▼
   Índice vectorial + grafo    ← camada derivada (retrieval, nunca SoT)
```

- O utilizador edita **markdown**. Um processo de ETL incremental re-mineia e alinha o índice.
- O ETL é **idempotente**: o mesmo conteúdo produz o mesmo identificador (hash), pelo que
  re-correr não duplica.
- O índice serve **recall semântico**; para recall verbatim (um ID, uma palavra rara) usa-se
  pesquisa determinística (grep) sobre a SoT.

## Regras de fluxo

- **Promover warm → hot:** editar o ficheiro hot quando uma memória passa a ser necessária em
  cada sessão.
- **Despromover hot → warm:** remover a referência do ficheiro hot; o ficheiro warm fica intacto.
- **Decay:** não é automático — o utilizador valida em revisões periódicas. Ficheiros obsoletos
  ficam minados no índice e continuam recuperáveis.

## Quando usar cada mecanismo de retrieval

| Situação | Mecanismo |
|---|---|
| Ficheiro conhecido pelo nome/path | Leitura directa. |
| Termo verbatim, ID concreto, jargão raro | Pesquisa determinística (grep) sobre a SoT. |
| Pergunta semântica/conceptual cross-corpus | Pesquisa vectorial (índice derivado). |
| Facto sobre uma pessoa/projecto/relação | Consulta ao grafo de conhecimento. |
| Estado operacional (tarefas, entregas) | Base de dados transaccional (não o índice semântico). |

> *Regra dura:* nunca escrever manualmente no índice informação que existe num markdown.
> O fluxo é sempre editar markdown → ETL re-mineia → índice alinha. Escritas manuais
> introduzem *drift*.

## Trabalho multi-turn resiliente a falhas

Para iterações longas com risco de interrupção (debugging em terreno, sessões muito longas),
manter um **log de iteração** com estado actual, o que falhou, o que funcionou e pendentes.
Marcá-lo como activo num índice de topo, para que uma sessão retomada o leia primeiro.
Remover a marca quando a iteração fecha.
