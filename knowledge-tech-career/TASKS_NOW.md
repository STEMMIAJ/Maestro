# TASKS_NOW.md — Próxima rodada (pós-rodada 3)

Arquivo volátil. Sobrescrito a cada rodada. Contém apenas o que deve ser feito AGORA.

Data de corte: 2026-04-23.
Contexto: rodada 2 concluiu densificação de 6 blocos (190 MDs totais). Rodada 3 em execução paralela fechando 03, 04, 05, 10, 16 + integração PYTHON-BASE + pesquisa TODO/RESEARCH. Tarefas abaixo valem para a rodada 4.

## Prioridade alta (fazer na próxima rodada)

1. **IDX-001** — Rodar `openclaw memory index --path /Users/jesus/Desktop/STEMMIA\ Dexter/knowledge-tech-career/` e validar saída. Se comando falhar, documentar erro exato e marcar `TODO/RESEARCH` em `14_automation/openclaw_jobs/`.
2. **Validação symlink** — `ls -la 02_programming/python/python-base` deve retornar link vivo. Ler 1 falha de `python-base/03-FALHAS-SOLUCOES/db/falhas.json` como teste.
3. **KTC-142** — Criar 1 script Python real a partir de uma spec em `14_automation/scripts/`. Prova de conceito. Rodar e capturar output.
4. **Completar blocos esqueleto remanescentes** — Se rodada 3 não terminou 03/04/05/10, despachar agentes complementares.
5. **Promoção de rascunhos** — Revisar manualmente 5 artefatos densos dos blocos 01/02/06/07/08/11 e promover para `status: vigente` no frontmatter.

## Prioridade média

6. **Git local** — Inicializar repositório dentro de `knowledge-tech-career/` OU adicionar como parte do git do Dexter (decisão humana). Primeiro commit com tag `v0.2.0`.
7. **GitHub privado** — Criar repositório `knowledge-tech-career` privado e push inicial. Proteger branch main.
8. **Piloto 16_inbox** — Importar 1 conversa ChatGPT ou Claude para `16_inbox/raw_conversations/` usando formato definido em `00_governance/promotion_rules.md` (se existir; caso contrário, criar regra primeiro).

## Prioridade baixa

9. **Resolver TODO/RESEARCH acumulados** — Preços de certificação (AWS, CompTIA, HL7), dados de mercado TI-BR, comandos exatos OpenClaw na versão instalada.
10. **Snapshot rodada 4** — Ao final, gravar `13_reports/snapshots/progress_snapshot_round3.md` ou `_round4.md` conforme sequência.

## Regras desta rodada

- **Antes de qualquer coisa:** rodar contagem `find ... -name "*.md" | wc -l` para confirmar término da rodada 3.
- Não promover rascunho sem frontmatter revisado e fonte citada em `12_sources/`.
- Toda tarefa concluída: mudar status em `TASKS_MASTER.md` para `EXECUTADO` e somar ao `CHANGELOG.md` em novo bloco `[0.3.0]`.
- Fila oficial de trabalho: `~/Desktop/_MESA/40-CLAUDE/fila-opus/dexter-maestro/fila.md`.
- Ao final: reescrever este arquivo com as 5–10 próximas.
