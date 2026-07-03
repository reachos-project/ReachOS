# 05 — Guardrails (defence-in-depth)

> **Âmbito.** Este documento descreve o **padrão** de defesa em profundidade em conceito.
> Não inclui regras de detecção reais nem esqueletos executáveis — publicar assinaturas de
> detecção dá reconnaissance a um atacante. Adapta o conceito ao teu ambiente.

## Ideia central

Nenhum controlo isolado é suficiente. A defesa faz-se por **camadas independentes**: se uma
falha ou é contornada, outra apanha. O objectivo é que a probabilidade conjunta de uma acção
destrutiva passar todas as camadas seja praticamente nula.

## As três camadas

```
Acção proposta pelo agente
        │
        ▼
[C1] Matcher de autorização   ── autoriza/nega por padrão estático (allow/deny)
        │  (passou)
        ▼
[C2] Inspecção de conteúdo    ── examina o comando/ficheiro em profundidade antes de executar
        │  (passou)
        ▼
[C3] Backups + reversibilidade ── mesmo que algo passe, é recuperável
        │
        ▼
   Execução
```

### C1 — Matcher de autorização (no limiar da ferramenta)

Uma lista de regras `allow`/`deny` avaliadas estaticamente sobre a acção pedida. Rápida e
determinística. **Limitação importante:** só intercepta no limiar coordenador→ferramenta.
Comandos **embutidos dentro de um script** não atravessam este matcher — correm como qualquer
binário. Daí a necessidade das camadas seguintes.

### C2 — Inspecção de conteúdo (pre-execução)

Um hook que recebe a acção antes de esta ocorrer e a examina em profundidade:

- Extrai o comando de forma **robusta** (parsing estruturado, não regex frágil que pára na
  primeira aspa escapada).
- Deteta operações destrutivas sobre paths críticos, mesmo referenciadas indirectamente
  (como argumento de outro comando).
- **Fail-safe:** se a análise falhar (input malformado), bloqueia por precaução (over-block)
  em vez de deixar passar.
- Convenção de saída: código 0 = permitir, código ≠ 0 = bloquear, com a razão do bloqueio
  enviada para o canal de erro (para o modelo/operador a ver).

### C3 — Backups + reversibilidade

Antes de qualquer operação capaz de destruir configuração crítica, um backup verificável
(arquivo + manifesto de hashes) é criado e a sua integridade confirmada. A fonte-de-verdade em
markdown e um histórico de actividade append-only garantem que quase tudo é reversível.

## Padrões de guardrail comuns

| Guardrail | O que faz |
|---|---|
| **Workspace enforcement** | Um agente só pode escrever no seu workspace; escrita fora é negada e registada. |
| **Base de dados read-only por defeito** | Operações destrutivas de SQL (DELETE/DROP/etc.) bloqueadas; leitura livre. |
| **Verificação de URL** | Antes de recomendar/contactar um URL, exigir vários sinais de legitimidade convergentes. |
| **Protecção de segredos** | Bloquear a exposição ou leitura de ficheiros de credenciais. |
| **Deny-by-default em paths críticos** | Ficheiros de configuração/identidade são negados por defeito para escrita, com uma janela de manutenção explícita e curta. |

## Princípios

1. **Camadas independentes** — cada uma falha de forma diferente; não partilham o mesmo ponto cego.
2. **Fail-safe / over-block** — na dúvida, bloquear.
3. **Registar tudo** — cada negação e cada excepção autorizada vai para um log auditável.
4. **Nunca confiar na identidade auto-reportada** de um chamador para decisões de segurança.
5. **A regra concreta não é pública** — o *padrão* é partilhável; as assinaturas de detecção não.
