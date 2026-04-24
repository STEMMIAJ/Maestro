---
name: Unificação STEMMIA (captação→laudo + banco aprendizado)
description: Plano-mestre de 12 tarefas para unificar todo o ecossistema pericial no Dexter, criar Fluxo D (laudo) inexistente, e banco SQLite de aprendizado contínuo
type: project
originSessionId: 052d369f-79e0-4813-a943-277edb5d3fe3
---
# Unificação STEMMIA — iniciado 2026-04-17

**Plano:** `~/Desktop/STEMMIA Dexter/00-CONTROLE/PLANO-UNIFICACAO-2026-04-17.md`

## Estado atual (mapeado nesta sessão)
- Hub Dexter: 4.7GB, já estruturado (FERRAMENTAS, MODELOS, BANCO-DADOS, MUTIRÃO, painel, hooks, agents, n8n, memoria)
- ANALISADOR FINAL: 4.2GB, contém scripts/ e processos/
- 300 scripts Python (142 Desktop + 158 stemmia-forense)
- Fluxos A/B/C documentados em `STEMMIA — SISTEMA COMPLETO/`
- Fluxo D (Laudo) NÃO EXISTE — precisa criar
- Banco aprendizado NÃO EXISTE — só Chrome profile DBs
- 683Gi livres (1TB confirmado)

## 4 Fases
- F0: Inventário + mapas (duplicatas, deps, lacunas) — Tasks 1-2
- F1: Consolidação (decisões + execução) — Tasks 3-4
- F2: Revisar A,B,C + criar D — Tasks 5-8
- F3: Banco SQLite + hooks captura + RAG — Tasks 9-11
- F4: Dashboard + skill /stemmia — Task 12

## Decisões locked-in
- Hub único = Dexter (já é, manter)
- Banco aprendizado = SQLite em `BANCO-DADOS/aprendizado.db`
- 4 tabelas: errors, successes, patterns, contexts
- Captura via UserPromptSubmit hook (estende sistema anti-mentira existente)
- RAG via SessionStart hook injetando TOP-10 lições
- NUNCA rm — sempre mv para _arquivo/
- Commit git a cada fase

## Estimativa
12-17 dias úteis (~3h/dia)

## Próxima ação
Executar Task 1 (inventariar.py) — depende só de Python3 já instalado
