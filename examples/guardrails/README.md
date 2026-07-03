# Exemplos de guardrails (esqueletos)

> **Leia primeiro.** Estes ficheiros são **esqueletos ilustrativos**, não hooks prontos a
> correr. Servem para mostrar a *forma* de um guardrail — a estrutura, a convenção de saída, o
> ponto de decisão. **Não** contêm as regras de detecção reais de nenhum sistema:
>
> - Os conjuntos de verbos destrutivos, os globs de paths críticos e as expressões de detecção
>   estão representados por **tokens** (`{{...}}`, `<...>`) que **cada instalação preenche**.
> - Os ficheiros `.pseudo.*` **não são executáveis como estão** — os tokens partem
>   deliberadamente qualquer tentativa de execução directa. Isto é intencional: um exemplo de
>   segurança não deve poder ser corrido às cegas contra um sistema real.
>
> Ver `patterns/defense-in-depth/` para a explicação do porquê as assinaturas concretas ficam
> privadas (evasão) e o padrão fica público (Kerckhoffs).

## Ficheiros

| Ficheiro | Camada | O que ilustra |
|---|---|---|
| `workspace-enforcement.pseudo.sh` | C1/C2 | Um agente só escreve no seu workspace; escrita fora → negar. |
| `content-inspection.pseudo.py` | C2 | Inspecção de conteúdo pré-execução com extracção robusta e fail-safe. |
| `sql-readonly.pseudo.sh` | C2 | Base de dados read-only por defeito; só leituras passam. |

## Convenção de saída (comum a todos)

- `exit 0` → **permitir** a acção.
- `exit != 0` → **bloquear**, com a razão escrita no canal de erro (stderr).
- Em caso de dúvida (input malformado, parser falha) → **bloquear** (fail-safe / over-block).
