# Pipeline Pericial — Stemmia Forense

## Fluxo de Etapas

```
NOMEACAO → PENDENTE-ACEITE → PENDENTE-PDF → PENDENTE-EXTRACAO → PENDENTE-ANALISE → PENDENTE-PROPOSTA → PENDENTE-AGENDAMENTO → PERICIA-AGENDADA → PERICIA-REALIZADA → PENDENTE-LAUDO → COMPLETO
                                                                                                                                                                    ↘ EM-CONTESTACAO → COMPLETO
```

## Etapas e Acoes

| Etapa | Acao do Perito | Prazo | Comando |
|-------|---------------|-------|---------|
| PENDENTE-ACEITE | Gerar peticao de aceite | 5 dias uteis (~7 corridos) da nomeacao | `/aceite` |
| PENDENTE-PDF | Baixar PDF do processo no PJe | — | manual (PJe Windows) |
| PENDENTE-EXTRACAO | Extrair texto do PDF | — | `pdftotext` |
| PENDENTE-ANALISE | Rodar analise completa | — | `/cowork` ou analise rapida |
| PENDENTE-PROPOSTA | Gerar proposta de honorarios | 5 dias corridos | `/proposta` |
| PENDENTE-AGENDAMENTO | Gerar peticao de agendamento | — | `/agendar` |
| PERICIA-AGENDADA | Realizar exame presencial | Data agendada | — |
| PERICIA-REALIZADA | Exame feito, aguardando laudo | — | — |
| PENDENTE-LAUDO | Elaborar laudo pericial | 30 dias corridos | `/laudo` |
| EM-CONTESTACAO | Responder contestacao | 15 dias uteis (~21 corridos) | `/contestar` |
| COMPLETO | Nenhuma — processo concluido | — | — |

## Estados Inativos

| Estado | Significado |
|--------|-------------|
| EXPIRADO | Prazo de aceite venceu sem acao |
| CANCELADO | Juiz cancelou a nomeacao |
| RECUSADO | Perito recusou a nomeacao |
| VAZIO | Sem dados — precisa iniciar processamento |

## Como a Etapa e Determinada

A funcao `inferir_etapa_pipeline()` em `consolidar_processos.py` verifica a existencia de arquivos na pasta do processo:

1. Tem laudo? → COMPLETO
2. Tem contestacao? → EM-CONTESTACAO
3. Tem agendamento? → PERICIA-AGENDADA ou PERICIA-REALIZADA
4. Tem proposta? → PENDENTE-AGENDAMENTO
5. Tem analise? → PENDENTE-PROPOSTA
6. Tem texto extraido? → PENDENTE-ANALISE
7. Tem PDF? → PENDENTE-EXTRACAO
8. Tem aceite? → PENDENTE-PDF
9. Situacao AJ "AGUARDANDO ACEITE"? → PENDENTE-ACEITE
10. Default → PENDENTE-PDF ou VAZIO

## Urgencia no Dashboard

O dashboard (`gerar_dashboard_hub.py`) calcula urgencia baseado em:

| Urgencia | Criterio | Cor |
|----------|----------|-----|
| VENCIDO | Prazo da etapa ja passou | Vermelho (#7f1d1d) |
| URGENTE | Vence em 1-3 dias | Amarelo (#78350f) |
| NORMAL | Vence em 4-15 dias | Azul (#1e3a5f) |
| SEM_PRAZO | Etapa sem prazo definido | Neutro (#1e293b) |

## Adicionar Nova Etapa

1. Adicionar em `CORES_ETAPA` no `gerar_dashboard_hub.py`
2. Adicionar em `ETAPAS_KANBAN` (ordem visual)
3. Adicionar label curto em `ETAPA_LABELS`
4. Se tiver prazo, adicionar em `PRAZOS_ETAPA`
5. Atualizar `inferir_etapa_pipeline()` em `consolidar_processos.py`
