# NEXT_SESSION_CONTEXT — Maestro

**Atualizado:** 2026-04-24 (fechamento sessao 4)
**Status sessao 4:** OPCAO B executada (pipeline /pericia funcional). FASE 0+1+3 fechadas. Bloqueio B1 ainda manual.

---

## Ao voltar, abra nesta ordem

1. `Maestro/PERMISSOES.md` — politica v2 (allow tudo exceto destrutivo)
2. `Maestro/HANDOFF-2026-04-24-SESSAO-04.md` — **fonte unica** de estado
3. `Maestro/TASKS_NOW.md`
4. `Maestro/FLOWS/USAGE-pericia.md` — como usar `/pericia <CNJ>`
5. `Maestro/futuro/B1-resolucao.md` — se quiser aplicar B1 manualmente

---

## Estado em 1 linha

Pipeline `/pericia` operacional (validado dry-run CNJ `0012022-56.2012.8.13.0059`), 5/5 deps OK, OpenClaw 138 processos no SQLite, conversa Perplexity intacta (4440 linhas), B1 doc pronto aguardando aplicacao manual, raiz Maestro limpa (4 legados em `legado-bootstrap/`).

---

## Verificacao minima (30s)

```sh
cd "$HOME/Desktop/STEMMIA Dexter/Maestro"
./bin/pericia 0012022-56.2012.8.13.0059 --dry-run        # esperado: exit 0, 5 deps OK
openclaw --version                                        # esperado: 2026.4.21
sqlite3 banco-local/maestro.db "SELECT COUNT(*) FROM processos;"   # esperado: 138
test -s .env && echo ".env OK"                            # esperado: ".env OK"
ls legado-bootstrap/ | wc -l                              # esperado: 4
```

---

## 5 acoes possiveis (escolher 1 na sessao 5)

1. **TESTE-REAL-B** — rodar pipeline `./bin/pericia <CNJ>` real num processo recente (5-15 min). Voce escolhe CNJ.
2. **B1** — aplicar plist gateway (5 min, manual seguindo `futuro/B1-resolucao.md` ou ordem `ativa launchctl B1` em chat).
3. **OPCAO A** — FASE 4 P6 integrador Perplexity → MEMORY (~25 min).
4. **OPCAO C** — verificador peticao com ancoragem PDF (~40 min).
5. **MANUTENCAO** — rotate device antigo (B2), aprovar pairing (B3), nao-bloqueantes.

---

## Regra de preservacao (inegociavel)

`conversations/raw/perplexity_conversation_2026-04-22_full.md` NAO sera alterada. MEMORY.md sera INDICE com ponteiros `[fonte: raw linhas NNNN-NNNN]`, nao resumo. Aplicar quando OPCAO A rodar.

---

## Adiados (NAO fazer sem ordem explicita)

- FASE 7 cron heartbeat — ordem: `ativa cron`
- FASE 8 deploy FTP stemmia.com.br — ordem: `deploy FTP`
- FASE 9 Telegram bot — ordem: `roda bot`
- B1 launchctl reload — ordem: `ativa launchctl B1`
