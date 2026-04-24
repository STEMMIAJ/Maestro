# FLOW 06 — Backup

## Objetivo

Garantir cópia segura e recuperável do estado do Maestro em três camadas progressivas, sem tocar dados de pacientes.

## Gatilho

- Fim de rodada (manual obrigatório).
- Cron J02 (diário 23h) quando ativo.
- Manual: "fazer backup do Maestro".

## Entradas

| artefato | caminho | observação |
|----------|---------|------------|
| Raiz Maestro | `~/Desktop/STEMMIA Dexter/Maestro/` | excluir `data/` |
| Destino local | `~/Desktop/STEMMIA Dexter/_arquivo/backups/maestro_YYYY-MM-DD/` | criado se não existir |
| Repo git | `.git/` na raiz de STEMMIA Dexter | para camada 2 |

## Passos

### Camada 1 — Local (disponível agora)

1. Criar destino: `mkdir -p "$HOME/Desktop/STEMMIA Dexter/_arquivo/backups/maestro_$(date +%Y-%m-%d)"`.
2. Executar:
   ```bash
   rsync -av --exclude 'data/' \
     "$HOME/Desktop/STEMMIA Dexter/Maestro/" \
     "$HOME/Desktop/STEMMIA Dexter/_arquivo/backups/maestro_$(date +%Y-%m-%d)/"
   ```
3. Verificar tamanho do destino com `du -sh`.
4. Logar em `logs/flow_06_YYYY-MM-DD.log`.

### Camada 2 — Git local (disponível com autorização)

5. `git -C "$HOME/Desktop/STEMMIA Dexter" add Maestro/`.
6. `git -C "$HOME/Desktop/STEMMIA Dexter" commit -m "maestro(backup): snapshot YYYY-MM-DD"`.
7. Não fazer push sem ordem explícita do Dr. Jesus.

### Camada 3 — Remoto cifrado (RESEARCH)

8. [TODO/RESEARCH] Dump criptografado para área restrita em `stemmia.com.br`.
9. Decisão pendente em `reports/database_options_initial.md`.
10. Nunca subir sem criptografia local antes.

## Saídas

| artefato | caminho |
|----------|---------|
| Backup local | `_arquivo/backups/maestro_YYYY-MM-DD/` |
| Commit git | histórico do repo pai |
| Log | `logs/flow_06_YYYY-MM-DD.log` |

## Falhas conhecidas / Rollback

| falha | sintoma | rollback |
|-------|---------|----------|
| `data/` incluída no rsync | pacientes expostos | abortar; verificar filtro `--exclude` antes de rodar |
| Destino sem espaço | rsync falha | verificar `df -h` antes; alertar Dr. Jesus |
| Commit com PII | dados reais no git | `git reset --soft HEAD~1`; corrigir; recomitar |
| Backup remoto sem criptografia | dado exposto | não subir; camada 3 bloqueada até decisão |

## Regras fixas

- **Nunca** incluir `data/` em nenhuma camada.
- Backup remoto: cifrado localmente antes de subir (chave em `~/.config/maestro/`).
- Testar restore semestralmente (manual): restaurar para `/tmp/maestro_test/` e verificar integridade.
- Retenção local: manter últimos 30 backups; purgar manualmente os mais antigos.

## Status

- Camada 1: disponível (manual).
- Camada 2: disponível com autorização explícita.
- Camada 3: pendente de decisão (RESEARCH).
- Cron J02: planejado, não ativo.
