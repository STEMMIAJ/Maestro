---
name: N8N Análise Pericial — Estado do Projeto
description: Pipeline de análise processual pericial completa — estado, limitações do n8n cloud, e pipeline local funcional
type: project
---

## Pipeline de Análise Pericial Automatizada

**Status:** Pipeline LOCAL funcional (19/mar/2026). Pipeline N8N cloud BLOQUEADO.

### Pipeline Local (FUNCIONA)
- Caminho: `~/Desktop/ANALISADOR FINAL/n8n-fluxo/TESTE-LOCAL/`
- Atalho: `~/Desktop/analisar-processo` (symlink)
- Uso: `bash ~/Desktop/analisar-processo processo.pdf`
- 8 etapas: Extração → Triagem (18 fatores) → 5 Verificadores → Merge → Gemini API → Relatório → Organização → Telegram
- Testado com GVImpugnacaoReagendar.pdf (7 págs, 19K chars, OK)

### N8N Cloud (BLOQUEADO)
- URL: https://n8n.srv19105.nvhm.cloud (nuvemIDC, v2.2.6)
- `executeCommand` não existe nesta versão
- Code node bloqueia módulos nativos (fs, os, child_process)
- **Para desbloquear:** adicionar `NODE_FUNCTION_ALLOW_BUILTIN=child_process,fs,os,path` no painel nuvemhospedagem e reiniciar

**Why:** O n8n cloud é hosting gerenciado, não VPS com root. Restrições de segurança impedem execução de shell/Python.

**How to apply:** Usar pipeline local para análises. Se quiser migrar para n8n, precisa configurar variáveis de ambiente ou contratar VPS self-hosted.

### Workflow JSON (pronto, não ativado)
- `~/Desktop/ANALISADOR FINAL/n8n-fluxo/workflow-analise-pericial-completo.json` (22 nós, 125 KB)
- Importável quando executeCommand for habilitado

### Scripts (12 arquivos)
- 4.1, 4.3, 4.4 (chunks, cobertura, síntese)
- verificador_cids_datasus.py (base CSV DataSUS)
- verificador_datas/nomes/medicamentos/exames.py
- merge_verificadores.py
- triagem_complexidade.py (862 linhas, substituiu score numérico 0-100)
- FRAMEWORK-COMPLEXIDADE-E-VERIFICADOR.md

### ETAPA 6 — Mudança Importante
- Score numérico 0-100 DESCONTINUADO
- Substituído por triagem factual: FATO + PROVA + IMPACTO
- Cada argumento de honorários tem lastro nos autos
