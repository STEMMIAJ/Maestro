# FLOW 02 — Auditoria do STEMMIA Dexter

## Objetivo

Varrer periodicamente o ecossistema `~/Desktop/STEMMIA Dexter/` para detectar: pastas abandonadas, scripts órfãos, duplicatas e tamanhos anormais. Produzir relatórios sem alterar nada fora de `reports/`.

## Gatilho

- Comando manual: "auditar Dexter" ou "rodar DEXTER-AUDITOR".
- Cron semanal J03 (domingo 20h) — planejado, não ativo.
- Cron mensal J05 (dia 1) para detecção de projetos parados >30 dias.

## Entradas

| artefato | caminho | observação |
|----------|---------|------------|
| Raiz Dexter | `~/Desktop/STEMMIA Dexter/` | leitura recursiva |
| Exclusões | `data/`, `MUTIRAO/`, `PROCESSOS-PENDENTES/` | nunca percorrer |
| Índice Python | `PYTHON-BASE/INDICE.md` | referência para detectar scripts não indexados |
| Último relatório | `reports/dexter_audit_*.md` (mais recente) | para diff |

## Passos

1. Listar todas as pastas em `~/Desktop/STEMMIA Dexter/` com `find` (excluindo `data/`, `MUTIRAO/`, `PROCESSOS-PENDENTES/`).
2. Coletar: data de última modificação, tamanho total por pasta.
3. Identificar pastas sem modificação há >30 dias → lista "candidatos a arquivo".
4. Listar todos os `.py` e cruzar com `PYTHON-BASE/INDICE.md` → orphans.
5. Detectar duplicatas por nome de arquivo (hash SHA256 quando viável).
6. Detectar arquivos >50 MB que não são PDFs ou ZIPs esperados.
7. Escrever:
   - `reports/dexter_audit_YYYY-MM-DD.md` (resumo geral)
   - `reports/dexter_duplicates_YYYY-MM-DD.md` (lista de duplicatas)
   - `reports/dexter_orphans_YYYY-MM-DD.md` (scripts não referenciados)
8. Logar execução em `logs/flow_02_YYYY-MM-DD.log`.

## Saídas

| artefato | caminho |
|----------|---------|
| Relatório geral | `reports/dexter_audit_YYYY-MM-DD.md` |
| Duplicatas | `reports/dexter_duplicates_YYYY-MM-DD.md` |
| Órfãos | `reports/dexter_orphans_YYYY-MM-DD.md` |
| Log de execução | `logs/flow_02_YYYY-MM-DD.log` |

Zero alterações no filesystem fora de `reports/` e `logs/`.

## Falhas conhecidas / Rollback

| falha | sintoma | rollback |
|-------|---------|----------|
| `find` lento por pasta grande | timeout >5min | limitar com `-maxdepth 4` |
| SHA256 em massa consome CPU | pico >80% | desativar hash, usar só nome |
| Exclusões não aplicadas | `data/` aparece no relatório | abortar, corrigir filtro, não publicar |
| Script `audit_dexter.py` ausente | ImportError | executar manualmente com Bash; script no backlog B008 |

## Status

- Planejado.
- Script `scripts/audit_dexter.py`: ainda não criado (backlog B008).
- Primeira execução: pendente.
