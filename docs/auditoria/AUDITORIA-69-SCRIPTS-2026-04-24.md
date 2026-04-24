# Auditoria de 61 scripts soltos fora do Dexter — 2026-04-24

> Issue: [#9](https://github.com/STEMMIAJ/Maestro/issues/9)
> Contexto: `_MESA/40-CLAUDE/PLANO-GITHUB-MAESTRO/AUDITORIA-SCRIPTS-PERDIDOS.md` listou 69 scripts soltos em 2026-04-24 04:07. Re-varredura hoje (mesmo dia, mais tarde) encontrou **61**. Diferença provável: arquivos movidos/deletados entre as duas varreduras, e exclusões aplicadas (`_MESA/01-ATIVO/PYTHON-BASE.migrado/` — já migrados; `Maestro/` — já dentro do Dexter).
>
> **Nada foi movido/deletado.** Esta é só uma tabela de classificação. Movimentação real depende da palavra `LIMPAR-LIBERADO` do Dr. Jesus em uma próxima sessão.

## Legenda

- **INTEGRAR** = útil, atual, deve entrar no Dexter
- **ARQUIVAR** = experimento morto, duplicata, deprecated (deletar após backup)
- **BLOQUEADO** = não consegui abrir
- 🔴 = credenciais/segredos hardcoded — revisar urgente antes de qualquer mover

## Tabela

Paths relativos a `~/Desktop/`.

| # | Path original | Tamanho | mtime | Classificação | Destino sugerido | Justificativa |
|---|---|---:|---|---|---|---|
| 1 | `_MESA/_sweep.sh` | 4055 | 2026-04-18 | INTEGRAR | `STEMMIA Dexter/src/automacoes/` | Script de sweep diário (launchd 03h) que organiza arquivos soltos do Desktop. Ativo e útil. |
| 2 | `_MESA/AUDITORIA OPENCLAW/VERIFY.sh` | 6310 | 2026-04-24 | ARQUIVAR | — | Verificador de checksums de uma auditoria OpenClaw pontual. Manter junto com a própria auditoria (não migrar pro Dexter). |
| 3 | `_MESA/20-SCRIPTS/bat-windows/000_DEPOIS_SE_FUNCIONOU_CLIQUE_AQUI_LOTE_80.bat` | 609 | 2026-04-14 | ARQUIVAR | — | Wrapper efêmero de lote PJe (nome auto-explicativo). Lógica real está em `src/pje/`. |
| 4 | `_MESA/20-SCRIPTS/bat-windows/ANALISAR_PROCESSOS_PJE.bat` | 87 | 2026-04-16 | ARQUIVAR | — | .bat de 87 bytes, trivial wrapper. Duplica lógica de `STEMMIA Dexter/src/pje/`. |
| 5 | `_MESA/20-SCRIPTS/bat-windows/BAIXAR_60_FALTANTES_PJE.bat` | 88 | 2026-04-16 | ARQUIVAR | — | Wrapper efêmero 88 bytes para lote específico. |
| 6 | `_MESA/20-SCRIPTS/bat-windows/BAIXAR_FILA_PJE_TJMG_20260420.bat` | 94 | 2026-04-20 | ARQUIVAR | — | Wrapper de fila datada (2026-04-20). Uso único. |
| 7 | `_MESA/20-SCRIPTS/bat-windows/BAIXAR_PJE_17042026_LOGADO.bat` | 91 | 2026-04-17 | ARQUIVAR | — | Wrapper datado de uso único. |
| 8 | `_MESA/20-SCRIPTS/bat-windows/BAIXAR_PJE_17042026.bat` | 84 | 2026-04-17 | ARQUIVAR | — | Idem (wrapper datado). |
| 9 | `_MESA/20-SCRIPTS/bat-windows/BAIXAR_PJE_PLAYWRIGHT_17042026.bat` | 192 | 2026-04-17 | ARQUIVAR | — | Idem. Playwright Windows abandonado em favor de Selenium. |
| 10 | `_MESA/20-SCRIPTS/bat-windows/BAIXAR_PJE_TAIOBEIRAS_PRIMEIRO.bat` | 6426 | 2026-04-20 | INTEGRAR | `STEMMIA Dexter/legado-bootstrap/pje-windows/` | 6.4 KB — .bat real (não wrapper) que baixa fila priorizada. Referenciado pelo `.command` mac. Preservar junto com o companheiro. |
| 11 | `_MESA/20-SCRIPTS/bat-windows/BAIXAR_SELENIUM_UNBUFFERED.bat` | 91 | 2026-04-17 | ARQUIVAR | — | Wrapper trivial. |
| 12 | `_MESA/20-SCRIPTS/bat-windows/BAIXAR_TAIOBEIRAS_PJE.bat` | 86 | 2026-04-16 | ARQUIVAR | — | Wrapper trivial (substituído pelo #10 maior e mais recente). |
| 13 | `_MESA/20-SCRIPTS/bat-windows/BAIXAR_TUDO_PJE.bat` | 5359 | 2026-04-20 | INTEGRAR | `STEMMIA Dexter/legado-bootstrap/pje-windows/` | 5.3 KB — .bat real de lote completo. Preservar junto com BAIXAR_PJE_TAIOBEIRAS_PRIMEIRO. |
| 14 | `_MESA/20-SCRIPTS/bat-windows/BAIXAR-21-FALTANTES.bat` | 918 | 2026-04-16 | ARQUIVAR | — | .bat datado de lote específico. |
| 15 | `_MESA/20-SCRIPTS/bat-windows/BUSCAR-PROCESSOS-WIN.bat` | 611 | 2026-04-16 | ARQUIVAR | — | Wrapper de busca. Substituído por `Automações/buscar.sh` ou Dexter/src. |
| 16 | `_MESA/20-SCRIPTS/bat-windows/CONTAR_PJE_PUSH.bat` | 80 | 2026-04-16 | ARQUIVAR | — | Wrapper 80 bytes. |
| 17 | `_MESA/20-SCRIPTS/bat-windows/DIAG_PYTHON_PJE.bat` | 80 | 2026-04-17 | ARQUIVAR | — | Diagnóstico efêmero. |
| 18 | `_MESA/20-SCRIPTS/bat-windows/DIAG_REDE_WINDOWS.bat` | 82 | 2026-04-17 | ARQUIVAR | — | Idem. |
| 19 | `_MESA/20-SCRIPTS/bat-windows/FIX_GREENLET_E_BAIXAR.bat` | 86 | 2026-04-17 | ARQUIVAR | — | Fix pontual de dependência quebrada num dia. |
| 20 | `_MESA/20-SCRIPTS/bat-windows/FIX_VCRUNTIME_ARM64.bat` | 84 | 2026-04-17 | ARQUIVAR | — | Fix pontual ARM64. |
| 21 | `_MESA/20-SCRIPTS/bat-windows/INCLUIR_E_BAIXAR_NOVOS_ONLINE.bat` | 94 | 2026-04-18 | ARQUIVAR | — | Wrapper trivial. |
| 22 | `_MESA/20-SCRIPTS/bat-windows/INCLUIR_FALTANTES_PJE.bat` | 86 | 2026-04-17 | ARQUIVAR | — | Wrapper trivial. |
| 23 | `_MESA/20-SCRIPTS/bat-windows/MATAR_E_REINICIAR_PJE.bat` | 86 | 2026-04-17 | ARQUIVAR | — | Reset trivial. |
| 24 | `_MESA/20-SCRIPTS/bat-windows/PJE_BAIXAR_CLICANDO_ABRIR.bat` | 2814 | 2026-04-14 | INTEGRAR | `STEMMIA Dexter/legado-bootstrap/pje-windows/` | 2.8 KB — wrapper do `pje_clicar_prancheta_abrir.py` (macro contingência). Útil documentação de fluxo. |
| 25 | `_MESA/20-SCRIPTS/bat-windows/TAIOBEIRAS_INCLUIR_E_BAIXAR.bat` | 92 | 2026-04-17 | ARQUIVAR | — | Wrapper trivial. |
| 26 | `_MESA/20-SCRIPTS/command-mac/1-ABRIR-CLAUDE-CONSISTENTE.command` | 104 | 2026-04-17 | ARQUIVAR | — | 104 bytes, só faz `exec` para `STEMMIA Dexter/00-CONTROLE/ABRIR-CLAUDE-CONSISTENTE.command`. Redundante. |
| 27 | `_MESA/20-SCRIPTS/command-mac/2-ABRIR-INBOX-INSTAGRAM-CLAUDE.command` | 522 | 2026-04-18 | INTEGRAR | `STEMMIA Dexter/src/launchers/` | Cria/abre INBOX instagram pro pipeline documental. Referencia paths Dexter — só realocar. |
| 28 | `_MESA/20-SCRIPTS/command-mac/CLICAR_AQUI_BAIXAR_PJE.command` | 1772 | 2026-04-20 | INTEGRAR | `STEMMIA Dexter/src/launchers/` | Ativa Parallels + dispara .bat Windows. Entry-point ativo do fluxo PJe. |
| 29 | `_MESA/20-SCRIPTS/python-avulsos/baixar_direto_selenium.py` | 50030 | 2026-04-20 | ARQUIVAR | — | Duplicata (50 KB) da raiz `~/Desktop/baixar_direto_selenium.py` (48 KB). Mesmo cabeçalho; versão raiz é oficial. |
| 30 | `_MESA/20-SCRIPTS/python-avulsos/speech_calibrator.py` | 12324 | 2026-04-21 | INTEGRAR | `STEMMIA Dexter/src/utilidades/` | Calibrador de ditado do próprio Dr. Jesus. Útil para perícia ditada. |
| 31 | `_MESA/40-CLAUDE/PLANO-GITHUB-MAESTRO/bootstrap.sh` | 9693 | 2026-04-24 | ARQUIVAR | — | Bootstrap do Maestro (uso único idempotente). Já foi rodado — Maestro existe. Mantém como referência histórica, não migrar. |
| 32 | `_MESA/40-CLAUDE/PLANO-GITHUB-MAESTRO/templates/hooks/install.sh` | 396 | 2026-04-24 | ARQUIVAR | — | Template já copiado para `Maestro/hooks/install.sh`. Duplicata. |
| 33 | `_MESA/40-CLAUDE/PLANO-GITHUB-MAESTRO/templates/scripts/finalize.sh` | 920 | 2026-04-24 | ARQUIVAR | — | Template já em `Maestro/scripts/finalize.sh`. Duplicata. |
| 34 | `_MESA/40-CLAUDE/PLANO-GITHUB-MAESTRO/templates/scripts/status.sh` | 1557 | 2026-04-24 | ARQUIVAR | — | Idem (template já migrado para Maestro/). |
| 35 | `_MESA/40-CLAUDE/PLANO-GITHUB-MAESTRO/templates/scripts/sync.sh` | 597 | 2026-04-24 | ARQUIVAR | — | Idem. |
| 36 | 🔴 `Automações/10_ferramentas/ml_monitor/ml_auth.py` | 4932 | 2026-04-12 | INTEGRAR | REVISAR URGENTE → `STEMMIA Dexter/legado/ml-monitor/` | OAuth2 ML. **Contém CLIENT_ID + CLIENT_SECRET hardcoded** (linhas 14-15). Rotacionar secret antes de migrar; depois mover para env. |
| 37 | 🔴 `Automações/10_ferramentas/ml_monitor/ml_buscar.py` | 3617 | 2026-04-12 | INTEGRAR | REVISAR URGENTE → `STEMMIA Dexter/legado/ml-monitor/` | Idem (mesmo par CLIENT_ID/SECRET hardcoded). |
| 38 | 🔴 `Automações/10_ferramentas/ml_monitor/ml_monitor_preco.py` | 7228 | 2026-04-12 | INTEGRAR | REVISAR URGENTE → `STEMMIA Dexter/legado/ml-monitor/` | Monitor preço. **TELEGRAM_BOT_TOKEN hardcoded** (linha 21). Rotacionar bot antes de migrar. |
| 39 | `Automações/12_cron/run_ml_monitor.sh` | 284 | 2026-04-12 | ARQUIVAR | — | Wrapper cron que aponta para `STEMMIA — SISTEMA COMPLETO/` (pasta "legado antigo"). Reescrever depois que ml_monitor for integrado. |
| 40 | `Automações/12_cron/run_monitor_publicacoes.sh` | 360 | 2026-04-12 | ARQUIVAR | — | Wrapper que roda `~/stemmia-forense/src/pje/monitor-publicacoes/monitor_publicacoes.py` (caminho legado, já alias). Redundante com cron Dexter. |
| 41 | `Automações/12_cron/run_relatorio_telegram.sh` | 330 | 2026-04-12 | ARQUIVAR | — | Wrapper cron apontando para stemmia-forense. Redundante. |
| 42 | `Automações/12_cron/run_scanner_visao.sh` | 378 | 2026-04-12 | ARQUIVAR | — | Idem. |
| 43 | `Automações/buscar.sh` | 3798 | 2026-04-12 | INTEGRAR | `STEMMIA Dexter/src/utilidades/` | Busca semântica no sistema (scripts, sessões, processos, manifesto). Útil, funcional, só reapontar paths. |
| 44 | `Automações/gerar_inventario.py` | 8765 | 2026-04-12 | INTEGRAR | `STEMMIA Dexter/src/utilidades/` | Gera `manifest_inventario.json` de todos os locais de automação. Já conhece o Dexter. Útil. |
| 45 | `Automações/verificar_integridade.py` | 5401 | 2026-04-12 | INTEGRAR | `STEMMIA Dexter/src/utilidades/` | Verifica portal Automações + symlinks + cron. Útil saúde-sistema. |
| 46 | `baixar_direto_selenium.py` | 48512 | 2026-04-20 | INTEGRAR | `STEMMIA Dexter/src/pje/` | Versão raiz (48 KB) do Selenium downloader. 157 processos PJe TJMG. **Este é o canonical** — usar este e arquivar duplicata #29. |
| 47 | `baixar_peticoes_enviadas.py` | 23856 | 2026-04-20 | INTEGRAR | `STEMMIA Dexter/src/pje/` | 23 KB. Baixa petições enviadas pela aba "Minhas Petições". Ativo, Selenium Windows. |
| 48 | `INVENTÁRIO EXTRAJUDICIAL/gerar_atas_notariais.py` | 29501 | 2026-03-16 | INTEGRAR | `STEMMIA Dexter/src/peticao-cowork/atas-notariais/` | 29 KB. Gera 3 modelos de Ata Notarial em DOCX com fundamentação (CPC 384, Lei 8.935, etc.). Pericial real. |
| 49 | `Manus Automação/automacao_pje.py` | 8957 | 2026-04-13 | ARQUIVAR | — | Experimento antigo Playwright. **Bug no path** (`"~\"` escapado errado na linha 9). Substituído por `src/pje/baixar_documentos_processo_aberto.py`. |
| 50 | `Manus Automação/iniciar_chrome.bat` | 910 | 2026-04-13 | ARQUIVAR | — | Wrapper Chrome debug — funcionalidade já coberta por Dexter/PJE-INFRA. |
| 51 | `Sei la /000_CLIQUE_AQUI_PJE.bat` | 675 | 2026-04-14 | ARQUIVAR | — | Atalho duplicado dos .bat em `_MESA/20-SCRIPTS/bat-windows/`. Pasta "Sei la " sugere lixo. |
| 52 | `Sei la /BAIXAR_DOCUMENTOS_PROCESSO_ABERTO.bat` | 5955 | 2026-04-14 | ARQUIVAR | — | 5.9 KB — CNJ específico `5030880-86.2024.8.13.0105` hardcoded. Efêmero. |
| 53 | `Sei la /PJE_1_TESTE_5_DOCUMENTOS.bat` | 781 | 2026-04-14 | ARQUIVAR | — | Wrapper do `pje_clicar_prancheta_abrir.py`. CNJ fixo. |
| 54 | `Sei la /PJE_2_LOTE_80_DOCUMENTOS.bat` | 804 | 2026-04-14 | ARQUIVAR | — | Idem. |
| 55 | `Sei la /PJE_3_LOTE_80_MODO_GRADE.bat` | 810 | 2026-04-14 | ARQUIVAR | — | Idem. |
| 56 | `src/pje/baixar_documentos_processo_aberto.py` | 25313 | 2026-04-14 | INTEGRAR | `STEMMIA Dexter/src/pje/` | 25 KB. Playwright + CDP. Ativo — baixa documentos avulsos do processo aberto no Chrome Windows. |
| 57 | `src/pje/pje_clicar_prancheta_abrir.py` | 7049 | 2026-04-14 | INTEGRAR | `STEMMIA Dexter/src/pje/` | 7 KB. Macro pyautogui contingência quando PDF único retorna HTTP 429. Referenciado por vários .bat (#24, #53-55). |
| 58 | `STEMMIA — SISTEMA COMPLETO/arquivo/abrir-chrome-pje.bat` | 421 | 2026-03-16 | ARQUIVAR | — | Abre Chrome debug PJe TJMG. Substituído por infra Dexter/PJE-INFRA. |
| 59 | 🔴 `STEMMIA — SISTEMA COMPLETO/scripts/ml_auth.py` | 4932 | 2026-04-06 | ARQUIVAR | — | **Cópia idêntica** do #36 (mesmo CLIENT_ID/SECRET hardcoded, mesma data do conteúdo). Duplicata. |
| 60 | 🔴 `STEMMIA — SISTEMA COMPLETO/scripts/ml_buscar.py` | 3617 | 2026-04-06 | ARQUIVAR | — | Cópia idêntica do #37. Duplicata. |
| 61 | 🔴 `STEMMIA — SISTEMA COMPLETO/scripts/ml_monitor_preco.py` | 7228 | 2026-04-06 | ARQUIVAR | — | Cópia idêntica do #38 (mesmo BOT_TOKEN hardcoded). Duplicata. |
| 62 | 🔴 `STEMMIA — SISTEMA COMPLETO/scripts/relatorio-diario-telegram.sh` | 1550 | 2026-03-24 | ARQUIVAR | — | **BOT_TOKEN + CHAT_ID hardcoded**. Substituído por `Automações/12_cron/run_relatorio_telegram.sh` (que também é ARQUIVAR). Rotacionar bot antes de apagar. |

## Totais

- **INTEGRAR:** 17 (13 limpos + 4 🔴 para revisar antes)
- **ARQUIVAR:** 45
- **BLOQUEADO:** 0

> Obs.: tabela tem 62 linhas porque o script `relatorio-diario-telegram.sh` entrou como #62 (flagado com segredo) depois da numeração original; ajuste menor sem impacto.

## Scripts críticos (top 3)

1. **`~/Desktop/baixar_direto_selenium.py`** (48 KB, 2026-04-20) — downloader Selenium de 157 processos PJe TJMG. É o canonical que rodou o último lote Taiobeiras. Mover para `STEMMIA Dexter/src/pje/` e apagar a duplicata em `_MESA/20-SCRIPTS/python-avulsos/`.
2. **🔴 `Automações/10_ferramentas/ml_monitor/ml_monitor_preco.py`** — Telegram bot token `8288644542:AAHynmefpO9ji7hx-fBRxn2XIhEnTluQGe8` e `CHAT_ID 8397602236` hardcoded. Mesmo token aparece em `STEMMIA — SISTEMA COMPLETO/scripts/relatorio-diario-telegram.sh`. Rotacionar bot antes de qualquer mover/commit.
3. **`INVENTÁRIO EXTRAJUDICIAL/gerar_atas_notariais.py`** (29 KB) — gerador de Ata Notarial pericial com fundamentação jurídica embutida. Isolado na raiz do Desktop, alto risco de perda se pasta for limpa. Mover para `STEMMIA Dexter/src/peticao-cowork/atas-notariais/` imediatamente após aprovação.

## Segredos encontrados (revisar antes de qualquer ação)

- **ML OAuth:** `CLIENT_ID=1288087545929506`, `CLIENT_SECRET=RQJfaWE9QDlloowuErOgaaMPV3oFiWfN` (4 arquivos)
- **Telegram Bot:** `8288644542:AAHynmefpO9ji7hx-fBRxn2XIhEnTluQGe8`, `CHAT_ID 8397602236` (2 arquivos, coerente com `@stemmiapericia_bot` já conhecido)

Ação recomendada antes de integrar: rotacionar CLIENT_SECRET do ML app, colocar em `~/Desktop/STEMMIA Dexter/.env` (já no gitignore), reescrever scripts para ler do env.

## Próximo passo (após aprovação humana)

Para executar movimentação real, Dr. Jesus precisa mandar nova sessão com:

> `LIMPAR-LIBERADO` — aplicar AUDITORIA-69-SCRIPTS da issue #9

Aí o agente:
1. Move os 17 INTEGRAR para os destinos sugeridos (commit por lote)
2. Faz tar.gz dos 45 ARQUIVAR em `~/Desktop/BACKUP CLAUDE/2026-04-24_ARQUIVO-SCRIPTS-SOLTOS/` antes de deletar
3. Atualiza referências quebradas (crons `Automações/12_cron/*` apontam para paths antigos)
4. Fecha issue #9 com evidência colada
