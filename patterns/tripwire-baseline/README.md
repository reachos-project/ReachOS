# Padrão: Tripwire + baseline com disciplina de rebaseline

> **Âmbito.** Engenharia de um tripwire de integridade sobre ficheiros críticos. O conjunto
> concreto de ficheiros vigiados (os globs) e os hashes reais **não** fazem parte do repo —
> revelam a topologia do sistema de confiança. Paths fictícios.

## Objectivo

Detectar **alterações não autorizadas** a ficheiros críticos (config do coordenador, regras,
hooks, perfis de sandbox) entre o momento em que se sabe que estão bons e agora.

## Mecanismo

1. **Baseline:** calcular um **manifesto de hashes** dos ficheiros críticos num estado
   conhecido-bom, e guardá-lo (pin).
2. **Tripwire:** periodicamente (e no arranque de sessão) **re-calcular** os hashes e comparar
   com o pin. Qualquer divergência → **alerta**.

```text
# PSEUDO-CÓDIGO — os globs vigiados são configuração da instalação, não deste repo.
pin  := load_manifest(BASELINE_PIN)        # { path: hash } de um estado conhecido-bom
now  := hash_all(WATCHED_GLOBS)            # WATCHED_GLOBS NÃO distribuído
drift := diff(pin, now)
if drift:
    alert("integridade: ficheiros mudaram vs baseline", drift)
```

## A parte difícil: disciplina de rebaseline

O tripwire só é útil se as alterações **legítimas** forem tratadas de forma disciplinada.
Senão, cada alteração autorizada dispara um alerta, o operador habitua-se a ignorar alertas
(**alert-fatigue**), e o tripwire perde valor exactamente quando é preciso.

Regra: **uma alteração autorizada a um ficheiro vigiado tem de disparar um rebaseline na mesma
sessão.** O fluxo:

```
Alteração autorizada a ficheiro vigiado
        │
        ▼
Re-calcular hash desse ficheiro  ──►  actualizar o pin (rebaseline)  ──►  registar quem/quando/porquê
        │
        ▼
O tripwire volta a estar "verde" para esse ficheiro
```

- Uma alteração **autorizada sem rebaseline** = alerta falso recorrente → erosão do sinal.
- Uma alteração **não autorizada** = drift sem rebaseline correspondente → alerta verdadeiro.

A distinção entre os dois casos é precisamente a existência (ou não) de um rebaseline
**registado e justificado** para aquela alteração.

## Controlo de dois lados (snapshot vs live)

Para apanhar tanto a alteração legítima esquecida como a maliciosa, comparar o estado **live**
contra um **snapshot** em dois momentos: no **arranque** da sessão (apanha alterações feitas
enquanto ninguém estava a ver, ex.: um processo que morreu a meio) e no **fecho** (apanha
alterações feitas durante a sessão e re-baseliza o snapshot). Se o arranque encontra drift sem
um fecho anterior que o justifique, isso é o caminho-de-crash — trazer à atenção do humano antes
de qualquer outra coisa.

## Princípios

1. **Baseline = estado conhecido-bom**, com pin versionado (mas os hashes reais fora do público).
2. **Alteração autorizada → rebaseline na mesma sessão**, senão alert-fatigue.
3. **Rebaseline é registado e justificado** — é o que distingue autorizado de malicioso.
4. **Controlo de dois lados** — arranque e fecho — para não haver janela cega.
5. **Os globs vigiados são privados** — publicá-los diz ao atacante o que evitar tocar.
