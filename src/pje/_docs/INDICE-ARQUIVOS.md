# Índice de Arquivos — src/pje/

Lista completa dos arquivos da pasta unificada com 1 linha de descrição cada.
Gerado em 2026-04-19. Atualizar quando adicionar/remover arquivo.

---

## Raiz `src/pje/`

| Arquivo | Descrição |
|---|---|
| `README.md` | Hub central — porta de entrada da pasta, comandos rápidos, troubleshooting |
| `__init__.py` | Marca `pje` como pacote Python (vazio) |
| `atualizar-pje.py` | CLI legado: `--listar`, `--extrair-texto`, `--baixar`. Delega para `baixar_pje` legado, com guardas (janela TJMG, validação PDF, quarentena) |
| `pje_standalone.py` | CLI standalone Playwright: `--aj`, `--ajg`, `--baixar`, `--tudo`. Não depende do Parallels (só AJ/AJG) |

## `common/` — helpers reutilizáveis

| Arquivo | Descrição |
|---|---|
| `common/__init__.py` | Marca `common` como pacote |
| `common/browser.py` | Dispatcher: `abrir_browser(motor='local'\|'remoto')` |
| `common/cdp.py` | `chrome_debug_vivo`, `cdp_url` — checagem do Chrome debug |
| `common/cnj.py` | `RE_CNJ`, `validar_cnj`, `limpar_cnj`, `safe_filename_cnj` |
| `common/config.py` | `SETTINGS` dataclass lendo variáveis do ambiente (dotenv) |
| `common/download.py` | `clicar_e_salvar_download` com fallback nova aba |
| `common/janela.py` | `dentro_janela_tjmg`, `msg_janela` — janela 13h-19h |
| `common/logger.py` | `JobLogger.captura_falha` → JSONL + REGISTRO.md (integra falhas.json) |
| `common/paths.py` | `processos_dir`, `quarentena_dir`, `safe_move` (cross-FS via copy2+unlink) |
| `common/pdf.py` | `pdf_valido`, `extrair_texto`, `cnj_no_pdf` |
| `common/pje_session.py` | `sessao_ativa`, `salvar_diagnostico` |
| `common/richfaces.py` | `escapar_id`, `setar_select_jsf`, `aguardar_select_populado` (PrimeFaces) |

## `config/` — configuração central unificada

| Arquivo | Descrição |
|---|---|
| `config/__init__.py` | Marca `config` como pacote |
| `config/config_pje.py` | URLs PJe, timeouts, paths, credenciais via env — ponto único de verdade (criado 19/abr/2026) |
| `config/config_validacao.py` | Validações de CNJ/comarca/formatos |

## `descoberta/` — FLUXO 1: descoberta de CNJs novos

| Arquivo | Descrição |
|---|---|
| `descoberta/__init__.py` | Marca pacote |
| `descoberta/README.md` | 12 blocos lógicos detalhando cada fonte e etapa |
| `descoberta/descobrir_processos.py` | 1234 linhas, orquestra 6 fontes em paralelo (ThreadPoolExecutor max 6) |
| `descoberta/blacklist_manual.txt` | CNJs em que Dr. Jesus é PARTE (não perito); popular manualmente da Consulta Pública TJMG |
| `descoberta/core/__init__.py` | Marca pacote |
| `descoberta/core/filtro_perito.py` | Classifica PERITO / PARTE / INDETERMINADO (criado 19/abr/2026) |
| `descoberta/fontes/__init__.py` | Marca pacote |
| `descoberta/fontes/consulta_publica_tjmg.py` | Módulo isolado da fonte Consulta Pública TJMG (JSF/Seam com ViewState) |
| `descoberta/fontes-cache/consulta_publica_tjmg_12785885660.json` | Cache da última resposta para o CPF do perito |

## `download/` — FLUXO 2: download de PDFs no Windows

| Arquivo | Descrição |
|---|---|
| `download/README.md` | 13 blocos lógicos detalhando Selenium, dedup persistente, paginação RichFaces |
| `download/baixar_push_pje.py` | 1344 linhas — Selenium + Chrome debug 9223, dedup persistente via `_downloads_feitos.json` (fix 19/abr) |
| `download/pje_verificacao.py` | Verifica conteúdo do PDF (CNJ na primeira página), Telegram notifications, `janela_disponivel()` |

## `cadastro/` — FLUXO 3: cadastra CNJs no PUSH

| Arquivo | Descrição |
|---|---|
| `cadastro/README.md` | 10 blocos lógicos detalhando Playwright, login VidaaS, seletores CSS fallback |
| `cadastro/incluir_push.py` | Playwright (async), cadastra lote de CNJs na aba PUSH do PJe TJMG, detecta duplicata/erro |
| `cadastro/mapear_paginas_push.py` | Varre todas as páginas do PUSH e gera mapa JSON dos CNJs já cadastrados (pré-filtro anti-duplicata) |

## `renomear/` — futuro

| Arquivo | Descrição |
|---|---|
| `renomear/renomear_cidades.py.TODO` | Esqueleto para renomear pastas por cidade; precisa lista de variações (GV/Mantena/Taiobeiras etc.) |

## `_logs/` — relatórios diários consolidados

| Arquivo | Descrição |
|---|---|
| `_logs/relatorio-2026-04-19.md` | Relatório consolidado do dia (descoberta + downloads + cadastros + alertas) |

## `_sessoes/` — sínteses de sessão Claude

| Arquivo | Descrição |
|---|---|
| `_sessoes/SESSAO-2026-04-19-unificacao-fluxos.md` | Síntese da unificação dos 3 fluxos + skill `/novo-fluxo` |

## `_docs/` — documentação auxiliar

| Arquivo | Descrição |
|---|---|
| `_docs/DIAGRAMA-FLUXO.md` | Diagrama ASCII ponta-a-ponta do pipeline PJe |
| `_docs/INDICE-ARQUIVOS.md` | Este arquivo |
| `_docs/HISTORICO.md` | Changelog cronológico (16/abr → 19/abr/2026) |

## Arquivos invisíveis (dot-files)

| Arquivo | Descrição |
|---|---|
| `.env.example` | Template de variáveis de ambiente (`PJE_MOTOR`, `TELEGRAM_TOKEN` etc.) — copiar para `.env` |
| `.gitkeep` | Placeholder para manter pasta versionada no git |

---

Total aproximado: ~40 arquivos. Lista gerada via `find src/pje -type f -not -path '*/\.*' -not -path '*__pycache__*' | sort`.
