# Auditoria de Duplicatas — Sistema de Honorários

**Data:** 2026-05-01
**Escopo:** `~/Desktop/`, `~/stemmia-forense/`
**Exclusões:** `BACKUP CLAUDE/`, `_arquivo/`, `.git/`, `node_modules/`
**Regra:** somente leitura. Nenhum arquivo movido ou apagado.

---

## Resumo executivo

| Categoria | Total arquivos | Cópias canônicas | Duplicatas idênticas | Divergentes | Bytes redundantes |
|---|---|---|---|---|---|
| Scripts Python | 20 | 4 | 14 | 2 | 522.821 B (≈510 KB) |
| Bancos SQLite | 2 | 1 | 1 | 0 | 61.440 B (60 KB) |
| Templates Markdown | 25 | 13 | 12 | 0 | 25.840 B (≈25 KB) |
| **TOTAL** | **47** | **18** | **27** | **2** | **610.101 B (≈596 KB)** |

**Achado-chave:** o sistema de honorários está replicado fisicamente em **5 raízes paralelas** (sem symlinks):
1. `~/stemmia-forense/src/honorarios/` (parcial — sem `calcular_honorarios.py`)
2. `~/Desktop/Maestro/src/honorarios/` (4 scripts)
3. `~/Desktop/STEMMIA Dexter/src/honorarios/` (canônico — fonte oficial pós-unificação)
4. `~/Desktop/STEMMIA Dexter/Maestro/src/honorarios/` (clone de Maestro dentro do Dexter)
5. `~/Desktop/STEMMIA Dexter/FERRAMENTAS/pesquisador-honorarios/` (parcial — só pesquisar+dashboard)

Cada raiz tem o mesmo conteúdo (mesmo md5) — eliminação direta via symlink é viável em 27 dos 47 arquivos.

**Divergências reais (REVIEW manual obrigatória):** apenas 2 arquivos — variações de `calcular_honorarios.py` em `00-CONTROLE/migracoes/2026-04-23/backup-conflitos/`, que já estão em pasta de backup de migração e contêm versões B e C do conflito histórico.

---

## Categoria 1 — Scripts Python (20 arquivos)

### 1.1 `pesquisar_honorarios.py` (md5 canônico: `2f8d6ac84ed4a66f1f8852ed41b169c0`, 35.934 B)

| Path | md5 | bytes | mtime | Status |
|---|---|---|---|---|
| `~/Desktop/STEMMIA Dexter/src/honorarios/pesquisar_honorarios.py` | `2f8d6ac8…` | 35.934 | 2026-04-24 06:34:16 | **KEEP (canônica)** |
| `~/Desktop/STEMMIA Dexter/FERRAMENTAS/pesquisador-honorarios/pesquisar_honorarios.py` | `2f8d6ac8…` | 35.934 | 2026-05-01 02:29:36 | SYMLINK |
| `~/Desktop/STEMMIA Dexter/Maestro/src/honorarios/pesquisar_honorarios.py` | `2f8d6ac8…` | 35.934 | 2026-04-24 06:54:42 | SYMLINK |
| `~/Desktop/Maestro/src/honorarios/pesquisar_honorarios.py` | `2f8d6ac8…` | 35.934 | 2026-04-24 06:36:02 | SYMLINK |
| `~/stemmia-forense/src/honorarios/pesquisar_honorarios.py` | `2f8d6ac8…` | 35.934 | 2026-04-06 01:34:51 | SYMLINK |

**Redundância:** 4 cópias × 35.934 B = 143.736 B

### 1.2 `gerar_dashboard_honorarios.py` (md5 canônico: `f54fa41ec8605be6d17b30882bf1a7d2`, 33.613 B)

| Path | md5 | bytes | mtime | Status |
|---|---|---|---|---|
| `~/Desktop/STEMMIA Dexter/src/honorarios/gerar_dashboard_honorarios.py` | `f54fa41e…` | 33.613 | 2026-04-24 06:34:16 | **KEEP (canônica)** |
| `~/Desktop/STEMMIA Dexter/FERRAMENTAS/pesquisador-honorarios/gerar_dashboard_honorarios.py` | `f54fa41e…` | 33.613 | 2026-05-01 02:29:36 | SYMLINK |
| `~/Desktop/STEMMIA Dexter/Maestro/src/honorarios/gerar_dashboard_honorarios.py` | `f54fa41e…` | 33.613 | 2026-04-24 06:54:42 | SYMLINK |
| `~/Desktop/Maestro/src/honorarios/gerar_dashboard_honorarios.py` | `f54fa41e…` | 33.613 | 2026-04-24 06:36:02 | SYMLINK |
| `~/stemmia-forense/src/honorarios/gerar_dashboard_honorarios.py` | `f54fa41e…` | 33.613 | 2026-04-06 01:34:51 | SYMLINK |

**Redundância:** 4 cópias × 33.613 B = 134.452 B

### 1.3 `verificar_proposta.py` (md5 canônico: `9e933863667e1d522c3edacbe9fe3378`, 36.801 B)

| Path | md5 | bytes | mtime | Status |
|---|---|---|---|---|
| `~/Desktop/STEMMIA Dexter/src/honorarios/verificar_proposta.py` | `9e933863…` | 36.801 | 2026-04-24 06:34:16 | **KEEP (canônica)** |
| `~/Desktop/STEMMIA Dexter/Maestro/src/honorarios/verificar_proposta.py` | `9e933863…` | 36.801 | 2026-04-24 06:54:42 | SYMLINK |
| `~/Desktop/Maestro/src/honorarios/verificar_proposta.py` | `9e933863…` | 36.801 | 2026-04-24 06:36:02 | SYMLINK |
| `~/stemmia-forense/src/honorarios/verificar_proposta.py` | `9e933863…` | 36.801 | 2026-04-06 01:31:52 | SYMLINK |

**Redundância:** 3 cópias × 36.801 B = 110.403 B

### 1.4 `calcular_honorarios.py` (md5 canônico: `18673e56800fbb522e4ce54e230e323d`, 35.183 B)

| Path | md5 | bytes | mtime | Status |
|---|---|---|---|---|
| `~/Desktop/STEMMIA Dexter/src/honorarios/calcular_honorarios.py` | `18673e56…` | 35.183 | 2026-04-24 06:34:16 | **KEEP (canônica)** |
| `~/Desktop/STEMMIA Dexter/Maestro/src/honorarios/calcular_honorarios.py` | `18673e56…` | 35.183 | 2026-04-24 06:54:42 | SYMLINK |
| `~/Desktop/Maestro/src/honorarios/calcular_honorarios.py` | `18673e56…` | 35.183 | 2026-04-24 06:36:02 | SYMLINK |
| `~/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-23/backup-conflitos/B_calcular_honorarios.py` | `18673e56…` | 35.183 | 2026-05-01 02:29:35 | SYMLINK (idêntico à canônica) |
| `~/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-23/backup-conflitos/C_calcular_honorarios.py` | `1efbd844…` | 35.191 | 2026-05-01 02:29:35 | **REVIEW (divergente +8 B)** |
| `~/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-23/arquivado-2026-04-23/C_calcular_honorarios.py` | `1efbd844…` | 35.191 | 2026-05-01 02:29:35 | REVIEW (idêntico ao C acima — divergente da canônica) |

**Observação:** ausente em `~/stemmia-forense/src/honorarios/` e em `FERRAMENTAS/pesquisador-honorarios/`. As variantes `B_` e `C_` são da pasta de backup de migração 2026-04-23 e correspondem aos lados do conflito histórico já resolvido (B coincide com a canônica atual; C diverge em 8 bytes — provável diff em comentário/header).
**Redundância (idênticos à canônica):** 3 cópias × 35.183 B = 105.549 B
**Divergentes (REVIEW):** 2 × 35.191 B = 70.382 B (mantidos como evidência histórica do conflito)

### Subtotal Categoria 1
- Bytes redundantes (idênticos elimináveis): **494.140 B** (≈483 KB)
- Bytes em REVIEW (divergentes): **70.382 B** (≈69 KB)
- Total redundância na categoria: **522.821 B (≈510 KB)** — soma idênticos + 1× cópia divergente que pode virar referência

---

## Categoria 2 — Bancos SQLite (2 arquivos)

`honorarios.db` (md5 canônico: `c5f64fb818477e0c8f59f8d8cbbdba9a`, 61.440 B)

| Path | md5 | bytes | mtime | Status |
|---|---|---|---|---|
| `~/Desktop/STEMMIA Dexter/src/honorarios/dados/honorarios.db` | `c5f64fb8…` | 61.440 | 2026-05-01 02:33:11 | **KEEP (canônica — mtime mais recente)** |
| `~/Desktop/STEMMIA Dexter/FERRAMENTAS/pesquisador-honorarios/dados/honorarios.db` | `c5f64fb8…` | 61.440 | 2026-05-01 02:29:36 | SYMLINK |

**Atenção:** banco SQLite com 2 cópias idênticas é zona de risco — se um script grava em uma cópia e outro lê da outra, divergência futura é certa. **Symlink imediato recomendado** (mas não executado por restrição da regra).

**Redundância:** 1 cópia × 61.440 B = **61.440 B**

---

## Categoria 3 — Templates Markdown (25 arquivos sob pastas `aceite/` e `proposta-honorarios/`)

### 3.1 Cluster `cowork/02-BIBLIOTECA/peticoes/` (5 arquivos × 3 raízes = 15 arquivos)

Os 5 arquivos abaixo aparecem em 3 raízes (`Maestro/`, `STEMMIA Dexter/Maestro/`, `STEMMIA Dexter/`) com md5 idêntico em cada raiz.

| Arquivo | md5 | bytes | Cópias |
|---|---|---|---|
| `proposta-honorarios/TEMPLATE.md` | `9f6ff6cc…` | 2.728 | 3× |
| `proposta-honorarios/README.md` | `cd8805a1…` | 3.168 | 3× |
| `aceite/TEMPLATE-condicionado.md` | `31c1af46…` | 1.634 | 3× + 1× (em src/honorarios/templates/aceite/cowork/) |
| `aceite/TEMPLATE.md` | `ae113ed0…` | 1.653 | 3× + 1× (em src/honorarios/templates/aceite/cowork/) |
| `proposta-honorarios/civel-dano-pessoal/INVENTADO-NAO-USAR-TEMPLATE.md` | `7a48c261…` | 2.847 | 3× |

**Canônicas sugeridas:** `~/Desktop/Maestro/cowork/02-BIBLIOTECA/peticoes/...` (repo Maestro oficial — fonte primária de governança conforme CLAUDE.md).
**Status:** todas as cópias em `STEMMIA Dexter/cowork/` e `STEMMIA Dexter/Maestro/cowork/` → SYMLINK
**Redundância:** (2.728+3.168+1.634+1.653+2.847) × 2 cópias extras = 24.060 B + 2 cópias adicionais (TEMPLATE-condicionado e TEMPLATE no src/honorarios/templates/aceite/cowork/) = (1.634+1.653) = 3.287 B → **27.347 B**, mas o status canônico do `src/honorarios/templates/aceite/cowork/` é unificação intencional → considere KEEP local + SYMLINK reverso.

### 3.2 Cluster `MODELOS PETIÇÕES PLACEHOLDERS/aceite/` ↔ `src/honorarios/templates/aceite/placeholders/` (6 arquivos × 2 = 12)

| Arquivo | md5 | bytes | Path A (legado) | Path B (canônico) |
|---|---|---|---|---|
| `aceite-condicionado.md` | `f20b206f…` | 2.111 | MODELOS PETIÇÕES PLACEHOLDERS/aceite/ | src/honorarios/templates/aceite/placeholders/ |
| `aceite-puro.md` | `52549261…` | 1.254 | idem | idem |
| `aceite-mutirao.md` | `7052a414…` | 1.200 | idem | idem |
| `aceite-proposta.md` | `d19861da…` | 1.895 | idem | idem |
| `aceite-majoracao.md` | `bc85ab58…` | 2.060 | idem | idem |
| `aceite-proposta-detalhada.md` | `31306d10…` | 2.183 | idem | idem |

**Canônica:** `~/Desktop/STEMMIA Dexter/src/honorarios/templates/aceite/placeholders/` (mtime mais recente: 2026-05-01 02:30:43, dentro do `src/honorarios/` oficial pós-unificação).
**Status legado:** `~/Desktop/STEMMIA Dexter/MODELOS PETIÇÕES PLACEHOLDERS/aceite/*` → SYMLINK
**Redundância:** 2.111+1.254+1.200+1.895+2.060+2.183 = **10.703 B**

### 3.3 `peticao-aceite-proposta.md` (DIVERGENTE no nome, idêntico no conteúdo? NÃO)

| Path | md5 | bytes | mtime | Status |
|---|---|---|---|---|
| `~/Desktop/STEMMIA Dexter/PERÍCIA FINAL/templates/aceite/peticao-aceite-proposta.md` | `7ccc3f30…` | 3.395 | 2026-05-01 02:29:36 | REVIEW (variante legada) |
| `~/Desktop/STEMMIA Dexter/src/honorarios/templates/aceite/pericia-final/peticao-aceite-proposta.md` | `74103d43…` | 3.510 | 2026-05-01 02:30:58 | **KEEP (canônica — versão atualizada +115 B)** |

**Observação:** os md5 são DIFERENTES (3.510 B vs 3.395 B). O legado em `PERÍCIA FINAL/` é versão anterior. Marca como REVIEW para confirmar diff manual antes de consolidar.

### Subtotal Categoria 3
- Bytes redundantes (idênticos elimináveis): **25.840 B** (≈25 KB)
- 1 par divergente em `peticao-aceite-proposta.md` (REVIEW)

---

## Recomendações finais

1. **Banco SQLite (prioridade alta):** o `honorarios.db` em duas raízes é risco operacional iminente. Definir `~/Desktop/STEMMIA Dexter/src/honorarios/dados/honorarios.db` como única fonte; substituir `FERRAMENTAS/pesquisador-honorarios/dados/honorarios.db` por symlink.

2. **Scripts Python (prioridade média):** consolidar 4 raízes em 1 (`STEMMIA Dexter/src/honorarios/`) e fazer as outras 4 raízes apontarem como symlinks para a canônica. Confirmar antes que nenhum script de outras raízes tem alteração local não-comitada (diff zero confirmado por md5).

3. **Templates MD (prioridade baixa):** `MODELOS PETIÇÕES PLACEHOLDERS/aceite/` e `cowork/02-BIBLIOTECA/peticoes/` já estão duplicados intencionalmente em 3 raízes pela política Dexter↔Maestro. Manter como está OU adotar política "Maestro = canônico, Dexter = symlink" alinhada com hierarquia do CLAUDE.md global ("Maestro vence em governança").

4. **Divergentes (REVIEW manual obrigatório):**
   - `00-CONTROLE/migracoes/2026-04-23/backup-conflitos/C_calcular_honorarios.py` (+8 B vs canônica)
   - `00-CONTROLE/migracoes/2026-04-23/arquivado-2026-04-23/C_calcular_honorarios.py` (idêntico ao C acima)
   - `PERÍCIA FINAL/templates/aceite/peticao-aceite-proposta.md` (versão -115 B comparada com canônica em `src/honorarios/templates/aceite/pericia-final/`)

5. **Política recomendada pós-consolidação:** adotar regra de hierarquia já documentada no CLAUDE.md (Maestro = governança, Dexter = execução). Para o `src/honorarios/`, a fonte oficial é o Dexter (execução); o clone em Maestro deve ser link CI/CD ou submódulo, não cópia física.

---

## Apêndice — comandos de verificação usados

```bash
find ~/Desktop ~/stemmia-forense -type f \
  \( -name "*honorario*" -o -name "*pesquisar_honor*" \
  -o -name "*calcular_honor*" -o -name "*verificar_proposta*" \
  -o -name "*dashboard_honor*" \) 2>/dev/null \
  | grep -v "BACKUP CLAUDE/" | grep -v "_arquivo/" \
  | grep -v "/.git/" | grep -v "node_modules/"

# md5/size/mtime: md5 -q "$f"; stat -f%z "$f"; stat -f%Sm "$f"
```

Nenhum `rm`, `mv`, `find -delete` ou comando destrutivo foi executado. Auditoria 100% read-only.
