# Histórico — src/pje/

Changelog cronológico da pasta unificada PJe. Do mais antigo ao mais recente.

---

## 2026-04-13 — Fix timeout_processo em `baixar_push_pje.py`

- **Problema:** processos grandes (>50MB) eram interrompidos em ~180s antes de completar o download
- **Fix:** elevado `TIMEOUT_PROCESSO` para 300s (5 min) e ajustado `aguardar_download` para
  verificar ausência de `.crdownload`/`.tmp` antes de retornar
- **Evidência:** download do primeiro lote completo (Selenium + Chrome debug 9223 + perfil isolado
  `~/Desktop/chrome-pje-profile`)
- **Memória:** `project_download_pje_139.md` (fluxo completo documentado)

---

## 2026-04-16 — Versão inicial de `descobrir_processos.py`

- **Origem:** `~/Desktop/ANALISADOR FINAL/scripts/descobrir_processos.py`
- **Função inicial:** consulta 4 fontes públicas (DJe TJMG, DataJud, Portal TJMG, PJe Consulta
  Pública), cruza com pastas locais `~/Desktop/ANALISADOR FINAL/processos/`, gera CSV consolidado
- **Problema residual:** retornava até 160 CNJs misturando PERITO + PARTE sem distinção
- **Memória:** `project_monitor_fontes.md` (uma das 5 fontes do monitor)

---

## 2026-04-17 — Fix verificação de conteúdo em `baixar_push_pje.py`

- **Problema:** bug de cache do PJe entregava PDF do processo ANTERIOR quando o download era
  disparado muito rápido. Dexter acumulava PDFs trocados — risco de laudo sobre caso errado
- **Fix:** após cada download, abre o PDF, extrai texto da 1ª página, busca CNJ via regex, compara
  com o esperado. Divergência → quarentena em `_invalidos/<CNJ>.pdf`
- **Função adicionada:** `verificar_conteudo()` em `pje_verificacao.py`
- **Evidência:** pasta `_invalidos/` passou a registrar PDFs trocados (antes eram salvos em cima)

---

## 2026-04-19 — Unificação + filtro PERITO/PARTE + skill `/novo-fluxo` + docs

Sessão grande, 6 agentes paralelos executando o plano `~/.claude/plans/binary-gliding-pine.md`.

### Criado

- **Pasta canônica `src/pje/`** como única fonte da verdade (antes: 5 pastas espalhadas)
- **`config/config_pje.py`** centralizado (URLs, timeouts, paths, credenciais via env — 5413 bytes)
- **`descoberta/core/filtro_perito.py`** classificando em PERITO / PARTE / INDETERMINADO (6561 bytes)
- **`descoberta/fontes/consulta_publica_tjmg.py`** módulo isolado da fonte JSF/Seam (6020 bytes)
- **`descoberta/blacklist_manual.txt`** lista manual de CNJs em que Dr. Jesus é parte (519 bytes,
  vazio — Dr. Jesus popula copiando da Consulta Pública TJMG)
- **Skill `/novo-fluxo`** + hook PostToolUse Write (automatiza criação de fluxo novo seguindo o
  padrão blocos-lógicos, 5 AND-conditions anti-desperdício de token)
- **Relatório diário 21h** em `_logs/relatorio-<data>.md` consolidando os 3 fluxos
- **Bot Telegram `/processos`** em `@stemmiapericia_bot` (ativo após reiniciar)
- **Symlinks** dos paths antigos apontando para esta pasta (retrocompatibilidade total)
- **READMEs por blocos lógicos** em `descoberta/` (12 blocos), `download/` (13 blocos),
  `cadastro/` (10 blocos)
- **`_docs/`** com `DIAGRAMA-FLUXO.md`, `INDICE-ARQUIVOS.md`, `HISTORICO.md` (este arquivo)
- **Síntese de sessão** em `_sessoes/SESSAO-2026-04-19-unificacao-fluxos.md`

### Corrigido

- **Loop infinito `baixar_push_pje.py`** — script baixava o mesmo CNJ 7× porque o PJe salva PDFs
  com nome hash (sem CNJ no filename), e a busca por "CNJ no nome" sempre falhava. Solução:
  `_DEDUP_INDEX` persistente em `_downloads_feitos.json` na pasta de download (linhas 78-135).
  Dedup agora opera em 3 camadas: `_CNJS_BAIXADOS_SESSAO` (set em memória), `_DEDUP_INDEX`
  (JSON persistente), `_encontrar_valido_existente` (conteúdo do PDF)

### Decisões arquiteturais

- Nada deletado — tudo preservado via symlink
- Ultraplan foi abandonado (timeout 90min) em favor de execução direta via Agent Teams paralelos
- READMEs em blocos lógicos (não linha-por-linha) para caber na memória comprometida do Dr. Jesus
- Consulta Pública TJMG usa ViewState JSF/Seam → blacklist manual como workaround (automação
  completa exige DevTools mapping futuro)

### Pendências herdadas

- Popular `blacklist_manual.txt` com CNJs da Consulta Pública TJMG
- `launchctl load` do plist de relatório diário (arquivo ainda não instalado)
- Reiniciar bot Telegram (processo antigo não conhece `/processos`)
- Criar `~/.credenciais-cnj.json` para AJ/AJG full
- Reativar `fonte_pje_trf6` (precisa DevTools para mapear ViewState correto — linha 1061 de
  `descobrir_processos.py`)

---

Manter este arquivo append-only. Cada alteração estrutural = uma entrada nova com data ISO e bullets
de criado/corrigido/decisões/pendências.
