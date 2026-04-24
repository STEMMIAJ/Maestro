# PROMPT COMPACTO — Retomar Maestro em sessao nova

Cole tudo abaixo em uma sessao nova do Claude Code. Contem o minimo para retomar a tarefa principal (FASE 1 + FASE 2 em paralelo) sem perder contexto.

---

```
Voce retoma o projeto Maestro (~/Desktop/STEMMIA Dexter/Maestro/).

CONTEXTO ESSENCIAL:
- Dr. Jesus = medico perito judicial, TEA+TDAH, sobrecarga, decisoes rapidas, PT-BR formal-seco, sem disclaimers.
- Maestro = governanca do ecossistema pericial Stemmia. Ingere conversas externas -> memoria operacional.
- Rodada 1 (2026-04-22) e Rodada 2 (2026-04-23): 100% concluidas. 9 fases operacionais pendentes.
- OpenClaw ja instalado localmente (v2026.4.2, 200MB em ~/.openclaw, auth Anthropic OK). Plano agora: backup + uninstall + reinstall limpo + integrar com Maestro.
- DB escolhido: JSON+SQLite hibrido (sem VPS, sem Supabase agora).
- LLM: OpenClaw roda determinista quando possivel; Haiku 4.5 quando precisa LLM; Opus so laudo final.

ARQUIVOS A LER NA ORDEM (obrigatorio, antes de qualquer acao):
1. Maestro/CHECKPOINT-2026-04-23.md (tasklist completa + status + %)
2. Maestro/PLANO-OPERACIONAL-2026-04-23.md (9 fases + 8 times paralelos + gantt + rollback)
3. Maestro/TASKS_NOW.md (proxima acao)
4. Maestro/futuro/04-CREDENCIAIS-PEDIR.md (o que esta bloqueando)
5. ~/Desktop/credenciais-maestro-2026-04-23.txt SE Dr. Jesus ja coletou (ver se existe)

TAREFA PRINCIPAL AGORA:
- Se Dr. Jesus disser "vai": disparar FASE 1 (backup ~/.openclaw) + FASE 2 (gh repo clone openclaw/openclaw) em PARALELO via 2 agentes general-purpose (Opus 4.7).
- FASE 1 para imediatamente antes de uninstall, aguarda decisao A/B/C do Dr. Jesus.
- FASE 2 roda completa sem bloqueio.

REGRAS HARD (nao negociaveis):
- Opus 4.7 para subagentes (CLAUDE_CODE_SUBAGENT_MODEL).
- Nao instalar/deletar sem confirmacao explicita.
- Nao inventar dados — tudo verificavel ou marcado TODO/RESEARCH.
- Sem acento/espaco/cedilha em paths de automacao.
- Consultar PYTHON-BASE/03-FALHAS-SOLUCOES/db/falhas.json antes de escrever Python.
- Se a skill guardar-futuro disparar ("guarda na pasta futuro"), usar.
- NAO commitar credenciais. .env fica em Maestro/ (fora do git).

BLOQUEIOS ATIVOS (credenciais vem do PROMPT-DR-JESUS-PARALELO.md em outra aba):
- BLK-A API key Anthropic
- BLK-B TOKEN Telegram + CHAT_ID
- BLK-C FTP nuvemhospedagem
- BLK-D Decisao A/B/C sobre ~/.openclaw

APOS LER OS 4 ARQUIVOS, responda em no maximo 5 linhas:
1. Em que fase estamos.
2. % atual.
3. O que depende do Dr. Jesus agora.
4. O que voce vai fazer em paralelo.
5. Pergunta unica: "vai?" ou "aguardo?"
```

---

## Como usar

1. `/clear` na sessao atual OU abrir nova sessao no mesmo repo.
2. Colar o bloco entre ``` acima.
3. IA le 4 arquivos, retorna status em 5 linhas.
4. Voce responde "vai" e IA dispara FASE 1 + FASE 2.

## Tamanho estimado

- Este prompt compactado: ~500 tokens (input).
- Leitura dos 4 arquivos referenciados: ~3000-5000 tokens (carregados sob demanda, nao ficam permanente no contexto se IA usar `Read` com limit).
- **Total para reiniciar a tarefa: ~3500-5500 tokens** vs 40-60k+ se continuar na sessao atual.
