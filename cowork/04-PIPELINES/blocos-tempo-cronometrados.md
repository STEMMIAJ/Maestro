---
nome: blocos-tempo-cronometrados
proposito: Regular rotina autista+TDAH com dor crônica. Cada tarefa vira bloco com início/fim previsíveis.
fundamentado_em: Pomodoro adaptado + research TEA/TDAH (transições de tarefa são o custo oculto)
---

# Blocos de tempo cronometrados — Rotina pericial regulável

## Por que existe

Perfil do usuário: TEA + TDAH + dores crônicas (ortopédicas/ósseas). O **maior inimigo** não é a tarefa — é:
1. **Não saber quanto vai durar** → adia indefinidamente.
2. **Não saber onde termina** → entra em hiperfoco e quebra o dia.
3. **Transições de tarefa** → custo cognitivo altíssimo, agrava dor por postura longa.

Solução: todo fluxo pericial tem **duração declarada**, **sinal de início** (Telegram/notificação), **sinal de fim obrigatório** (pausa), e **log automático** de desvio.

## Princípios

| Princípio | Aplicação |
|---|---|
| **Duração declarada ANTES de começar** | Todo pipeline MD tem `duracao_estimada:` no YAML. Sistema exibe no início. |
| **Timer visível** | Bloco tem contagem regressiva (via Bot Telegram ou menubar Mac). |
| **Pausa obrigatória** | Ao fim do bloco, sistema **bloqueia** continuação por 5-10min (hook `PostBlock`). |
| **1 bloco = 1 pipeline** | Não mistura análise + petição no mesmo bloco — fragmenta decisão. |
| **Troca de postura** | Na pausa, notificação sugere levantar/alongar/hidratar (custom para dor crônica). |
| **Log de desvio** | Se excedeu em >30%, sistema pergunta causa e alimenta estatística semanal. |

## Catálogo de blocos (duração padrão)

| Bloco | Pipeline | Duração | Intensidade cognitiva | Quando usar |
|---|---|---|---|---|
| **Triagem** | pipeline-analise-processo (passos 1-3: leitura + FICHA) | 25 min | Média | Manhã, energia intermediária |
| **Análise profunda** | pipeline-analise-processo (passos 4-8: verificações cruzadas) | 45 min | Alta | Início da manhã, pico de foco |
| **Petição simples** (aceite/agendamento) | pipeline-geracao-peticao (tipo=simples) | 15 min | Baixa | Qualquer momento, inclusive fim do dia |
| **Petição complexa** (proposta/esclarecimento) | pipeline-geracao-peticao (tipo=complexo) | 40 min | Alta | Manhã, após pausa de 15min |
| **Laudo — preâmbulo+histórico** | pipeline-geracao-laudo (passos 1-3) | 30 min | Média | Meio-manhã |
| **Laudo — discussão+conclusão** | pipeline-geracao-laudo (passos 4-6) | 60 min | Muito alta | **Pico de foco absoluto** (geralmente 9-11h ou 20-22h) |
| **Revisão** | pipeline-revisao-qualidade | 20 min | Baixa-Média | Final do dia, após pausa |
| **Exame físico (presencial)** | roteiro pericial + coleta | 45 min/periciando | Alta (social+física) | Manhã (sem dor acumulada do dia) |
| **Inbox/intimações** | pipeline-intimacao | 15 min | Baixa | Começo do dia, ritual inicial |
| **Arquivamento** | /arquivar | 10 min | Muito baixa | Fim de sexta, ritual de fechamento |

## Estrutura de um dia típico proposto (exemplo)

```
08:00  [15min] INTIMAÇÕES      — triagem, fila de prioridades
08:20  [25min] TRIAGEM         — 1 processo novo
08:50  PAUSA OBRIGATÓRIA (10min) — alongamento ombro/coluna
09:00  [45min] ANÁLISE PROFUNDA — continuar processo triado
09:50  PAUSA (15min)           — café, proteína, hidrata
10:10  [60min] LAUDO DISCUSSÃO — pico de foco
11:15  PAUSA (30min)           — almoço leve, deitar 10min (dor)
13:00  [40min] PETIÇÃO COMPLEXA — ex: proposta de honorários
13:45  PAUSA (15min)           — caminhar 5min
14:05  [15min] PETIÇÃO SIMPLES — aceite/agendamento backlog
14:25  PAUSA (10min)           — postura
14:40  [20min] REVISÃO         — verificar entregas do dia
15:00  FIM FORMAL DO TURNO PERICIAL
       (resto do dia: descanso ativo, outras demandas não-pericial)
```

Usuário pode ter rotina diferente — essa é uma **sugestão inicial** que o sistema ajusta com base em dados reais (hook `agendador-cognitivo`).

## Integração técnica

### 1. Cada pipeline MD declara no YAML
```yaml
duracao_estimada: 45 min
intensidade: alta
melhor_horario: [8:00-11:00, 20:00-22:00]
pausa_antes: 15 min (recomendada)
pausa_depois: 15 min (obrigatória)
```

### 2. Slash command `/bloco <nome>`
- Lê YAML do pipeline correspondente
- Envia notificação Telegram: "Iniciado bloco [TRIAGEM] — 25 min até [08:45]"
- Inicia timer (launchd + script em background)
- Ao fim: envia alerta, bloqueia retomada imediata por `pausa_depois` minutos

### 3. Hook `PostBlock` (`pos-bloco.sh`)
- Loga em `06-APRENDIZADO/blocos.jsonl`: `{data, bloco, duracao_declarada, duracao_real, desvio_pct, causa_desvio?}`
- Se desvio > 30%: pergunta causa via Telegram (opções: subestimei; interrompido; dor; distração; problema técnico)

### 4. Dashboard semanal
- Agrega `blocos.jsonl` e produz: % aderência, pipelines que estouram sempre (sugerir resplit), picos de foco do usuário (para agendador sugerir horários).

### 5. Modo "dor alta"
- Comando `/dor alta` reduz todos os blocos em 30% e força pausas duplas.
- Comando `/dor moderada` reduz em 15%.
- Sistema registra correlação dor × produtividade.

## Anti-padrões (o que NÃO fazer)

- ❌ "Só mais 5 min" virando 2 horas (quebra pausa obrigatória).
- ❌ Empilhar 3 pipelines de alta intensidade em sequência sem pausa (exaustão).
- ❌ Pular a revisão final (acumula dívida — sempre vira problema em 1-2 dias).
- ❌ Agendar bloco complexo depois de exame físico presencial (bateria social drena).
- ❌ Ignorar log de desvio ("não agora") — sistema precisa do dado para melhorar.

## Referências (a incorporar)

- Pomodoro clássico (25/5) adaptado: perícia exige blocos maiores (análise perde contexto em 25min).
- Coaching TDAH: "body-doubling" virtual (Claude fica ativo no terminal durante bloco = presença).
- Dor crônica: regra ergonômica dos 45min máximos sentado na mesma posição.
- TEA: previsibilidade absoluta de início/fim reduz ansiedade de antecipação.

## Próximos passos para ativar

1. [ ] Usuário valida catálogo de blocos acima (principalmente durações)
2. [ ] Implementar `/bloco <nome>` como slash command em `05-AUTOMACOES/slash-commands/`
3. [ ] Criar script timer em `05-AUTOMACOES/scripts/timer_bloco.py` (integra Telegram bot existente)
4. [ ] Hook `PostBlock` em `05-AUTOMACOES/hooks/pos-bloco.sh`
5. [ ] Dashboard semanal: agente que lê `blocos.jsonl` e emite relatório toda sexta 17h
