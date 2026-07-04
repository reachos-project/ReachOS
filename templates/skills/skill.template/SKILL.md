---
name: {{SKILL_NAME}}
description: "{{SKILL_DESCRIPTION}}"
user-invocable: {{SKILL_USER_INVOCABLE}}      # true / false
allowed-tools: [{{SKILL_ALLOWED_TOOLS}}]      # e.g.: "Read", "Bash", "Grep"
disallowed-tools: [{{SKILL_DISALLOWED_TOOLS}}]
model: {{SKILL_MODEL}}                         # e.g.: a lightweight model for checklists
---

<!--
  Skill template (reusable procedure/checklist).
  Replace every {{TOKEN}}. Keep the skill focused on a single responsibility.
-->

# {{SKILL_TITLE}}

## When to run

- **Mandatory** when {{SKILL_MANDATORY_TRIGGER}}.
- **Optional** for {{SKILL_OPTIONAL_TRIGGER}}.

## Input

- **Argument 1:** {{SKILL_INPUT_1}}.
- **Argument 2 (optional):** {{SKILL_INPUT_2}}.

## Procedure

1. {{SKILL_STEP_1}}
2. {{SKILL_STEP_2}}
3. {{SKILL_STEP_3}}

## Output

Present the result in a structured form:

```
=== {{SKILL_TITLE}}: <target> ===
Result: <summary>
Detail:
  - <item>: PASS / FAIL / WARN — reason
Recommendation: <action>
```

## Logging

After running, log the result to the transactional store to enable longitudinal
metrics (see `examples/db/schema.example.sql`).

## Notes

{{SKILL_NOTES}} — common pitfalls, dependencies, references to related rules.
