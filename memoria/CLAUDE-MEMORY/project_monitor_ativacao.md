---
name: Ativacao Monitor Movimentacoes (14/abr/2026)
description: Plano aprovado para ativar monitoramento diario automatizado de ~140 processos via DataJud + DJe + Comunica PJe + hub.py
type: project
originSessionId: c407ab45-7e03-456b-8b17-2f17757ff19a
---
# Ativacao do Monitor de Movimentacoes

**Data**: 2026-04-14
**Status**: PENDENTE — usuario aprovou, execucao nao iniciada

## O que ativar (3 frentes)

### 1. DataJud cron (codigo pronto, so ativar)
- Script: `~/stemmia-forense/scripts/monitor_completo.py`
- Consulta DataJud API para ~139 processos, detecta movimentacoes novas
- Precisa: criar launchd plist + configurar alerta Telegram
- Dados: compara com estado anterior, gera relatorio JSON

### 2. Comunica PJe (cadastro pendente)
- Script: `~/stemmia-forense/src/pje/monitor-publicacoes/comunica_pje.py`
- Fonte mais confiavel para intimacoes formais
- BLOQUEIO: falta cadastro em login.cnj.jus.br (gratuito, com certificado digital)
- Depois de cadastrar: ativar no config_hub.py

### 3. Hub de automacoes (debugar e ativar)
- Script: `~/stemmia-forense/automacoes/hub.py` (atualizado 14/abr/2026)
- Config: `~/stemmia-forense/automacoes/config_hub.py`
- Consolida DJe + DataJud + PJe Consulta em 4 fases
- Pasta logs vazia — nunca completou execucao
- Precisa: debugar, testar, criar cron

## Scripts ja funcionando (nao mexer)
- `descobrir_processos.py` — cron diario 6h (launchd ativo)
- `dje_tjmg.py` — via descobrir_processos
- `stemmia_bot.py` — bot Telegram ativo (launchd ativo)
- `consultar_aj.py` / `consultar_ajg.py` — funcionam com Chrome logado

## Fix PJe download (feito nesta sessao)
- Bug: paginacao usava `<a>` mas PJe/RichFaces usa `<span class="rf-ds-nmb">`
- Corrigido em `baixar_push_pje.py`: detectar_total_paginas, proxima_pagina, ir_pagina_direta
- PRECISA TESTAR — usuario vai rodar no Windows/Parallels
