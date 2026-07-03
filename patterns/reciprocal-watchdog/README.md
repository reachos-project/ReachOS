# Padrão: Watchdog recíproco (quem vigia o vigia)

> **Âmbito.** Engenharia do problema "quem vigia o vigilante". Canais de alarme reais e
> identidades de máquina ficam fora do repo.

## Problema

Um daemon de vigilância que morre **em silêncio** é pior do que não ter daemon nenhum: dá uma
falsa sensação de cobertura. Um processo confinado pode ser morto pelo SO, entrar em
circuit-breaker, ou ficar preso sem escrever. É preciso um sinal independente que detecte a
**ausência** do vigilante.

## Padrão

Dois sinais de liveness **independentes**, e um alarme que vive **fora** do sistema que está a
ser vigiado:

```
 Daemon vigiado  ──► actualiza ficheiro de liveness a cada tick
                                  │
      ┌───────────────────────────┘
      ▼
 Watchdog  ──► lê a idade do ficheiro de liveness
      │   está stale (não actualiza há > N)?
      ▼
 Empurra STALE / DEAD para um canal de alarme INDEPENDENTE do daemon vigiado
```

Regras de desenho:

- **Independência.** O watchdog não pode partilhar o destino do que vigia. Se ambos morrem pela
  mesma causa (mesmo processo, mesmo cron, mesma sandbox), não há vigilância real.
- **Estado fora do TCB vigiado.** O estado de liveness que o watchdog consulta vive **fora** do
  sistema de confiança que está a ser vigiado — senão comprometer o alvo compromete o
  observador.
- **Empurrar, não puxar.** O watchdog **empurra** o alarme (push) para um canal que o operador
  vê mesmo com o resto do sistema em baixo — não espera que alguém vá **puxar** (pull) o estado.
- **Alarme burro e externo.** A última camada é um alarme simples, externo e bem testado — não
  outra peça inteligente que também possa falhar.

## A regressão infinita, e onde parar

"Quem vigia o watchdog?" é uma regressão infinita. Não se resolve com mais uma camada
inteligente — resolve-se fazendo a **última** camada um alarme **externo, burro e trivialmente
verificável** (ex.: um serviço de notificação de terceiros que dispara se não receber um
sinal periódico). A fiabilidade vem da simplicidade e da externalidade, não de mais lógica.

## Princípios

1. **Detectar ausência, não só erro** — o silêncio é o modo de falha perigoso.
2. **Independência de destino** — vigia e vigiado não podem morrer juntos.
3. **Estado do observador fora do TCB vigiado.**
4. **Push para canal que sobrevive à queda do sistema.**
5. **A camada final é externa, burra e testada** — é aí que a regressão para.
