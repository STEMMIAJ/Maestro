# TASKS_NOW — Maestro

**Sessao:** 2026-04-24 (sessao 4 — auditoria + sincronizacao + B1)
**Pos:** sessoes 1-3 deixaram infra ~95% completa. Drift removido aqui.

---

## AGORA (caminho critico)

1. **[Voce]** decidir entre 3 opcoes operacionais — ver secao "Opcoes A/B/C" abaixo.
2. **[Claude]** executar opcao escolhida + fechar com FASE 3 (HANDOFF + NEXT_SESSION_CONTEXT + MEMORY).
3. **[Voce, manual]** aplicar B1 quando quiser (gateway API key persistente). Ver `futuro/B1-resolucao.md`.

## Opcoes A/B/C (escolher 1 — exclusivo, nao acumulativo nesta sessao)

| ID | O que faz | Tempo | Valor | Estado base |
|---|---|---|---|---|
| **A** | FASE 4 P6 integrador Sonnet 4.6 — indexa Perplexity em MEMORY.md como ponteiros `[fonte: raw linhas NNNN-NNNN]`, sem resumir | ~25 min | medio (preserva conteudo, evita perda futura) | `integrate_llm.py` 90% pronto em conversation_ingestion/ |
| **B** | Pipeline pericial minimo `/pericia [CNJ]` — cola scripts existentes (download → analise → laudo) em `FLOWS/pericia_completa.sh` | ~55 min | alto (valor real para pericias da semana) | esqueleto sh pronto |
| **C** | Verificador peticao com ancoragem PDF — anti-alucinacao em laudos | ~40 min | medio-alto | `verificadores/` 3 subpastas iniciais |

**Recomendacao:** B (maior valor real) ou A (menor risco, fecha P6 pendente desde sessao 2).

## % panorama geral
- Infraestrutura Maestro: **~95%** (B1 pendente; resto pronto)
- Pipeline operacional `/pericia`: **~30%** (depende OPCAO B)
- Integracao Perplexity → MEMORY: **~50%** (depende OPCAO A)
- Sistema integrado completo: **~40%** (cron, FTP, Telegram adiados conscientemente)

## Bloqueios atuais
- **B1** ANTHROPIC_API_KEY volatil no gateway — plist proposto + doc em `futuro/B1-resolucao.md`. Aplicacao manual ate ordem `ativa launchctl B1`.
- **B2** Device antigo precisa rotate (`openclaw devices rotate`) — nao-bloqueante.
- **B3** Pairing gateway scope — nao-bloqueante.

## Adiados (NAO fazer agora — registrados em futuro/)
- FASE 7 cron heartbeat (`futuro/FASE-7-CRON-HEARTBEAT.md`)
- FASE 8 deploy FTP stemmia.com.br
- FASE 9 Telegram bot Stemmia

## Proximo comando sugerido
> "ok escolho A" / "ok escolho B" / "ok escolho C"

## Referencias (ordem de leitura ao retomar)
1. `Maestro/PERMISSOES.md` (v2)
2. `Maestro/HANDOFF-2026-04-23-SESSAO-02.md` (estado verificado, decisoes tomadas)
3. Este arquivo
4. `Maestro/futuro/B1-resolucao.md` (manual)
5. `Maestro/legado-bootstrap/` (legados sessoes 1-3 — historico, nao instrucao)
