# Padrão: Defence-in-depth para acções destrutivas

> **Âmbito e limite de divulgação.** Este documento descreve a **engenharia** de um sistema
> de camadas que impede que uma acção destrutiva atinja ficheiros críticos. Descreve a *forma*
> — não as *assinaturas*. O conjunto concreto de regras de detecção (verbos, globs de path,
> expressões regulares) é **deliberadamente omitido**: publicar assinaturas de detecção ajuda a
> evasão. Princípio de Kerckhoffs aplicado ao contrário do óbvio — o *mecanismo* é público, a
> *configuração específica* de cada instalação é privada. Todos os paths abaixo são fictícios
> (`/opt/atlas/assistant/...`).

## Problema

Um agente de IA com acesso a uma shell pode, por engano ou por injecção, emitir uma operação
que apaga ou reescreve um ficheiro de configuração crítico (o ficheiro do coordenador, regras,
hooks, base de dados de estado). Um único ponto de controlo não chega — falha ou é contornado.
A resposta é fazer com que a acção tenha de atravessar **camadas independentes**, cada uma a
falhar de forma diferente.

## As três camadas

```
Acção proposta
   │
   ▼
[C1] Matcher de autorização (limiar da ferramenta)   allow / deny estático
   │ passou
   ▼
[C2] Inspecção de conteúdo (pré-execução)            examina em profundidade
   │ passou
   ▼
[C3] Backup verificável + fonte-de-verdade           recuperável mesmo que passe
   │
   ▼
Execução
```

### C1 — Matcher de autorização, e o seu ponto cego

O matcher avalia regras `allow`/`deny` estaticamente sobre a acção pedida. É rápido e
determinístico, mas tem um **ponto cego estrutural** que é a lição central deste padrão:

> O matcher só intercepta no **limiar coordenador → ferramenta**. Um comando destrutivo
> **embutido dentro de um script** que o coordenador manda executar **não** volta a passar pelo
> matcher — corre como qualquer outro binário do sistema.

Esta é uma propriedade genérica de qualquer matcher estático de limiar, não uma fraqueza de uma
implementação específica. É precisamente por isso que existem C2 e C3: a defesa não pode
depender só do limiar.

### C2 — Inspecção de conteúdo (pré-execução)

Um hook que recebe a acção **antes** de ela ocorrer e a examina. Requisitos de engenharia:

- **Extracção robusta do comando.** Ler o input estruturado da ferramenta (ex.: o campo do
  comando no payload JSON) com um parser real. **Nunca** com uma regex frágil que pára na
  primeira aspa escapada — um extractor frágil é um bypass à espera de acontecer.
- **Detecção de operações destrutivas sobre paths críticos**, incluindo referências
  *indirectas* (o path crítico como argumento de outro comando, ou passado a um script).
- **Fail-safe / over-block:** se o input for malformado ou o parser falhar, **bloquear** por
  precaução em vez de deixar passar.
- **Convenção de saída:** `exit 0` = permitir; `exit != 0` = bloquear, com a razão escrita no
  canal de erro para o modelo/operador a ver.

```text
# PSEUDO-CÓDIGO — não executável; assinaturas reais omitidas de propósito.
input      := parse_tool_payload(stdin)          # parser estruturado, não regex frágil
command    := input.command
if parser_failed:
    deny("payload malformado — over-block por precaução")   # fail-safe

# NOTA: DESTRUCTIVE_VERBS e CRITICAL_PATHS são conjuntos definidos por CADA instalação
#       e NÃO são distribuídos neste repo. Ver a nota de divulgação no topo.
if references_destructive_op(command, DESTRUCTIVE_VERBS) \
   and touches_any(command, CRITICAL_PATHS):
    deny("operação destrutiva sobre path crítico")
allow()
```

> **O que NÃO está aqui, e porquê.** O conteúdo de `DESTRUCTIVE_VERBS`, o de `CRITICAL_PATHS`,
> e a lógica de `references_destructive_op` são a *assinatura* do detector. Distribuí-los daria
> a um atacante o mapa exacto do que evitar. O padrão é partilhável; a assinatura não.

### C3 — Backup verificável + reversibilidade

Antes de qualquer operação capaz de destruir configuração crítica: criar um **backup
verificável** (arquivo + manifesto de hashes), **confirmar a integridade** do backup, e só
depois prosseguir. Combinado com uma **fonte-de-verdade em markdown** e um **histórico
append-only**, quase tudo fica reversível.

## Dois controlos de reforço que assentam sobre as camadas

### Validação pré-apply (dry-run de assumptions)

Antes de aplicar uma alteração a um ficheiro crítico, correr um dry-run que valida as
**premissas** da alteração contra o estado **actual**:

- cada item a REMOVER existe mesmo? (senão a alteração está obsoleta)
- cada item a ADICIONAR está ausente? (senão já foi aplicada)
- as premissas estruturais que a alteração assume ainda se verificam?
- a sintaxe das regras de permissão é válida? (uma regra com sintaxe inválida pode ser
  ignorada em silêncio pelo runtime — a defesa fica inactiva sem aviso)

Se houver **drift** entre o assumido e o real: **HALT** e reavaliar antes de aplicar.

### Backup-before-risky (pré-condição bloqueante)

Regra operacional: **nenhum** script — próprio ou entregue por um sub-agente — que contenha uma
operação destrutiva sobre um path crítico corre sem que antes exista um backup completo e
verificado. Um `syntax-check` (ex.: `bash -n`) **não** substitui a leitura semântica: é
obrigatório **ler** o script e procurar operações destrutivas referenciadas, incluindo
indirectamente. Se o script faz uma operação destrutiva sobre um path crítico, **devolver ao
autor** para redesenho — não executar.

## Porque é que camadas independentes compõem

Se cada camada falha de forma **independente** com probabilidade `p_i`, a probabilidade de uma
acção destrutiva atravessar todas é aproximadamente o **produto** `∏ p_i` — ordens de grandeza
menor do que qualquer camada isolada. A independência é o que importa: se duas camadas
partilham o mesmo ponto cego, não compõem. Desenhar cada camada para falhar por uma razão
diferente é o cerne do padrão.

## Princípios

1. **Camadas independentes** — pontos cegos diferentes.
2. **Fail-safe / over-block** — na dúvida, bloquear.
3. **Extracção robusta** — parser estruturado, nunca regex frágil.
4. **Nunca confiar na identidade auto-reportada** de um chamador para decisões de segurança.
5. **O padrão é público; a assinatura de detecção não é.**
6. **Backup verificado antes de qualquer operação destrutiva sobre um path crítico.**
