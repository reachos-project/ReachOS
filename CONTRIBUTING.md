# Contribuir para esta arquitectura de referência

Obrigado pelo interesse em contribuir. Este repositório é uma **arquitectura de referência** —
documenta *padrões* que uma organização pode estudar e reutilizar, com placeholders genéricos e
exemplos fictícios. Não é software pronto a correr. As contribuições mais úteis melhoram a
clareza, a correcção e a abrangência dos padrões, sem nunca trazer configuração viva de nenhum
sistema real.

## Como propor um padrão ou melhoria

1. **Abre uma issue** a descrever o padrão ou a melhoria antes de escrever muito código — para
   alinhar âmbito e evitar duplicação.
2. **Escreve de raiz (clean-room).** Descreve o padrão a partir do *conceito*. Nunca copies
   ficheiros, regras ou histórico de um deployment real — nem do teu.
3. **Usa placeholders e exemplos fictícios.** Tokens `{{MAIÚSCULAS_ENTRE_CHAVETAS}}` para
   valores parametrizáveis; entidades claramente inventadas (à semelhança de "Atlas Consulting")
   para exemplos. Ver os `templates/` e `examples/` existentes como modelo.
4. **Abre um pull request** com uma descrição do que o padrão resolve e de como se adapta.

## Regras de higiene (obrigatórias)

Estas regras protegem tanto este repositório como o teu próprio deployment:

- **Nunca submetas identificadores reais.** Sem paths pessoais, hostnames, IPs, endereços,
  tópicos de notificação, tokens, chaves, hashes de baseline, nem nomes de pessoas reais.
- **Nunca submetas regras de detecção reais** (assinaturas de sanitiser, globs de paths
  críticos, blocos de sandbox de um sistema em produção). O *padrão* é partilhável; a
  *assinatura* de detecção não — publicá-la ajuda a evasão. Ver `patterns/defense-in-depth/`.
- **Esqueletos não executáveis.** Exemplos de guardrails são ilustrativos e não devem poder
  correr às cegas contra um sistema real (ver `examples/guardrails/`).

## Verificação automática — linter anti-leak (CI)

Toda a contribuição passa por um **linter anti-leak** em integração contínua. O linter procura
identificadores reais (paths pessoais, hostnames, tokens, nomes internos) e sobreposições não
atribuídas com projectos upstream.

- **Critério de merge: 0 BLOCK.** Uma contribuição com qualquer resultado `BLOCK` não é
  integrada até ser corrigida.
- Resultados `WARN` (ex.: sobreposição de nome com um upstream) não bloqueiam, mas exigem que a
  sobreposição seja **consciente e atribuída** (ver `NOTICE`).

Corre o linter localmente antes de abrir o PR e confirma que o exit code é `0`.

## Licenciamento das contribuições

Ao submeter conteúdo a este repositório, o contribuidor certifica que:

(a) tem o direito de fazer a contribuição, e
(b) concede ao projecto uma licença irrevogável e perpétua para usar, reproduzir e distribuir a
    contribuição sob os termos deste repositório (Apache-2.0 / CC-BY-4.0, conforme aplicável).

Esta é uma certificação de origem no espírito do *Developer Certificate of Origin* (DCO): não
exige um contrato formal, apenas a garantia de que tens o direito de contribuir e de que a
contribuição fica sob as licenças do repositório. Ver `LICENSE`, `LICENSE-docs` e `NOTICE`.

## Estilo

- Documentação em português (PT-PT) com acentuação correcta; código, comentários e textos de
  licença em inglês.
- Estrutura clara, orientada ao padrão: o *porquê*, a *forma*, e os *princípios*.
- Sem marca nem referências a sistemas reais — a arquitectura transmite padrões, não instalações.
