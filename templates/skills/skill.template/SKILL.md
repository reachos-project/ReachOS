---
name: {{SKILL_NAME}}
description: "{{SKILL_DESCRIPTION}}"
user-invocable: {{SKILL_USER_INVOCABLE}}      # true / false
allowed-tools: [{{SKILL_ALLOWED_TOOLS}}]      # ex.: "Read", "Bash", "Grep"
disallowed-tools: [{{SKILL_DISALLOWED_TOOLS}}]
model: {{SKILL_MODEL}}                         # ex.: um modelo leve para checklists
---

<!--
  Template de skill (procedimento/checklist reutilizável).
  Substitui todos os {{TOKEN}}. Mantém a skill focada numa só responsabilidade.
-->

# {{SKILL_TITLE}}

## Quando executar

- **Obrigatório** quando {{SKILL_MANDATORY_TRIGGER}}.
- **Opcional** para {{SKILL_OPTIONAL_TRIGGER}}.

## Input

- **Argumento 1:** {{SKILL_INPUT_1}}.
- **Argumento 2 (opcional):** {{SKILL_INPUT_2}}.

## Procedimento

1. {{SKILL_STEP_1}}
2. {{SKILL_STEP_2}}
3. {{SKILL_STEP_3}}

## Output

Apresentar o resultado de forma estruturada:

```
=== {{SKILL_TITLE}}: <alvo> ===
Resultado: <resumo>
Detalhe:
  - <item>: PASS / FAIL / WARN — razão
Recomendação: <acção>
```

## Registo

Após correr, registar o resultado no store transaccional para permitir métricas
longitudinais (ver `examples/db/schema.example.sql`).

## Notas

{{SKILL_NOTES}} — armadilhas comuns, dependências, referências a regras relacionadas.
