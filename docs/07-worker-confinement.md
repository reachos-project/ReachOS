# 07 — Worker confinado com egress-allowlist

> **Âmbito.** Padrão para correr trabalho autónomo (um "worker") de forma isolada. Allowlists
> de hosts reais, chaves e runbooks de instalação ficam fora deste repo.

## Objectivo

Executar tarefas autónomas — potencialmente longas, potencialmente a partir de input não
totalmente confiável — sem dar ao worker acesso livre ao sistema nem à rede. O worker é uma
caixa com portas muito estreitas.

## Arquitectura

```
   Coordenador                         Worker confinado
       │  enfileira tarefa                    │
       ▼  (mensagem assinada)                 │
  ┌─────────┐   valida assinatura   ┌──────────────────┐
  │  FILA   │ ───────────────────► │  sandbox (FS/net │
  └─────────┘                       │  mínimos)         │
       ▲                            └────────┬──────────┘
       │ resultado                           │ rede de saída
       │                                     ▼
       │                            ┌──────────────────┐
       └─────────────────────────  │  EGRESS-PROXY     │
                                    │  (allowlist fecha-│
                                    │   da de hosts)    │
                                    └──────────────────┘
```

## Componentes

| Componente | Função |
|---|---|
| **Fila assinada** | O coordenador enfileira tarefas com uma assinatura (ex.: HMAC). O worker só executa mensagens com assinatura válida — impede injecção de trabalho. |
| **Sandbox do worker** | Perfil que restringe filesystem e rede ao mínimo necessário para a tarefa. |
| **Egress-proxy** | Toda a rede de saída passa por um proxy com **allowlist fechada** de hosts. Tudo o resto é negado e registado. |
| **Quarentena** | Input ou output suspeito é isolado numa área de quarentena em vez de processado. |
| **Limites de concorrência** | Um cap explícito de workers simultâneos, com um máximo duro acima do qual não se sobe sem revisão. |

## Porquê egress-allowlist (e não denylist)

Uma *denylist* falha por omissão — um host novo e malicioso passa. Uma **allowlist** falha
seguro: só o que está explicitamente permitido sai; tudo o resto é negado por defeito. Para
descobrir os hosts legítimos, corre-se a tarefa uma vez com allowlist mínima e observa-se o log
de negações para adicionar apenas os destinos genuinamente necessários.

## Instalação e go-live (conceito)

- Backup dos paths críticos **antes** de qualquer alteração de configuração do SO.
- Criar a árvore de trabalho com permissões restritas; a chave de assinatura com permissões `600`.
- Provar o confinamento com um teste testemunhado por um revisor de segurança antes do go-live.
- Toda a alteração a ficheiros críticos/arranque do SO é feita fora do fluxo automático,
  com backup prévio.

## Princípios

1. **Assinar o trabalho** — o worker não confia em qualquer mensagem, só nas assinadas.
2. **Egress por allowlist** — negar por defeito, permitir por excepção observada.
3. **Menor privilégio** — FS e rede reduzidos ao estritamente necessário.
4. **Provar antes de confiar** — teste de confinamento testemunhado antes de produção.
