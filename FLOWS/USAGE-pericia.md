# /pericia — Manual de uso

**Wrapper:** `Maestro/bin/pericia` → `Maestro/FLOWS/pericia_completa.sh`
**Validado:** 2026-04-24 02:42 (dry-run com CNJ real `0012022-56.2012.8.13.0059`, 5/5 deps OK, exit 0 valido / exit 1 invalido)

---

## Uso basico

```sh
cd "$HOME/Desktop/STEMMIA Dexter/Maestro"

# Verificar antes de rodar (zero risco):
./bin/pericia 5008297-73.2025.8.13.0105 --dry-run

# Rodar pipeline completo:
./bin/pericia 5008297-73.2025.8.13.0105

# Pular etapas:
./bin/pericia <CNJ> --pular-triagem        # se TEXTO-EXTRAIDO ja existe
./bin/pericia <CNJ> --skip-indexacao       # nao escreve em maestro.db
```

## Pipeline (5 etapas, fail-fast)

| # | Etapa | Script | Saida |
|---|---|---|---|
| 1 | Triagem PDF | `src/automacoes/triar_pdf.py enriquecer` | `TEXTO-EXTRAIDO.txt` |
| 2 | Analise paralela | `ANALISADOR FINAL/analisador de processos/pipeline_analise.py` | JSONs intermediarios |
| 3 | Consolidar FICHA | `consolidar_ficha.py` | `FICHA.json` |
| 4 | Honorarios | `calcular_honorarios.py --processo FICHA.json` | proposta honorarios |
| 5 | Indexar SQLite | `Maestro/banco-local/indexer_ficha.py --source <pasta>` | linha em `maestro.db` |

Se etapa N falhar (rc != 0), pipeline aborta e mostra log.

## Input esperado

Pasta deve existir em:
```
~/Desktop/ANALISADOR FINAL/processos/<CNJ>/
```

E ter pelo menos 1 PDF. Se faltar `TEXTO-EXTRAIDO.txt`, etapa 1 cria. Se ja existir, etapa 1 e pulada automaticamente.

## Onde nao roda

CNJs em `~/Desktop/ANALISADOR FINAL/analisador de processos/<CNJ>/` (pasta diferente, legado).
Se quiser rodar nesses, mover pasta primeiro para `processos/`:
```sh
mv "$HOME/Desktop/ANALISADOR FINAL/analisador de processos/<CNJ>" \
   "$HOME/Desktop/ANALISADOR FINAL/processos/"
```

## Logs

Cada execucao gera:
```
Maestro/logs/pericia-<CNJ>-YYYYMMDD-HHMMSS.log
```

Notificacao macOS no fim (Glass sound) — pode silenciar removendo linha 129 do `pericia_completa.sh`.

## Disponibilizar global (opcional, manual)

Para chamar `pericia` de qualquer pasta:
```sh
mkdir -p ~/bin
ln -sf "$HOME/Desktop/STEMMIA Dexter/Maestro/bin/pericia" ~/bin/pericia
# Garantir ~/bin no PATH (ja em zshrc se voce usou esse padrao)
```
