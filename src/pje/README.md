# PJe — Hub Unificado de Fluxos Periciais

Pasta canônica dos 3 fluxos de automação PJe TJMG do Dr. Jesus. Unificada em 19/abr/2026.

---

## Para Dr. Jesus (médico, TEA+TDAH, memória comprometida)

**Quando quiser rodar descoberta** (ver se tem processo novo no seu nome):
```bash
cd "~/Desktop/STEMMIA Dexter/src/pje/descoberta"
python3 descobrir_processos.py --sem-browser
```
Rodar no Mac, manhã ou à noite. Quanto tempo: ~2 min. Roda sozinho às 21h todo dia.

**Quando quiser baixar processos** (PDFs do PUSH do PJe):
```bash
# NO WINDOWS via Parallels (precisa cert A3)
python baixar_push_pje.py
```
Rodar SÓ no Windows/Parallels. PJe só funciona 13h-19h. Demora ~1min por processo.

**Quando quiser cadastrar no PUSH** (CNJs novos para receber intimação):
```bash
cd "~/Desktop/STEMMIA Dexter/src/pje/cadastro"
python3 incluir_push.py --dry-run     # testa
python3 incluir_push.py               # inclui pra valer
```
Rodar depois que descoberta achou CNJs novos. Login VidaaS manual (1x).

**Como saber se deu certo:**
- Descoberta: `descoberta/consolidado/RELATORIO_PROCESSOS_YYYY-MM-DD.csv` criado
- Download: PDFs em `~/Desktop/processos-pje-windows/` + `relatorio-*.json`
- Cadastro: mensagem "sucesso/incluído" na tela + `incluir_push_resultado_*.json`
- Relatório diário consolidado: `_logs/relatorio-YYYY-MM-DD.md` (21h)
- Telegram: bot `@stemmiapericia_bot` dispara notificação a cada marco

---

## Os 3 fluxos (o essencial)

1. **Descoberta** — descobre quais CNJs novos exigem ação. Roda 21h diário (launchd).
2. **Download** — baixa PDFs dos processos do PUSH. Roda manual no Windows/Parallels.
3. **Cadastro** — inclui CNJs no PUSH do PJe para receber intimações. Roda quando lista nova.

---

## Mapa de pastas (comentado)

```
src/pje/
├── README.md                          # este arquivo (hub)
├── __init__.py
├── .env.example                       # template de config (SETTINGS via env)
├── atualizar-pje.py                   # CLI legado (listar/extrair-texto/baixar)
├── pje_standalone.py                  # Playwright próprio para AJ/AJG
│
├── config/                            # Configuração central
│   ├── config_pje.py                  # URLs, paths, CPF, janela TJMG (fonte única)
│   └── config_validacao.py            # regras de validação
│
├── descoberta/                        # FLUXO 1 — descobrir CNJs novos
│   ├── descobrir_processos.py         # orquestrador (6 fontes paralelas)
│   ├── README.md                      # doc em blocos lógicos
│   ├── blacklist_manual.txt           # CNJs "sou parte, não sou perito" (Dr. Jesus popula)
│   ├── core/filtro_perito.py          # classifica PERITO / PARTE / INDETERMINADO
│   ├── fontes/consulta_publica_tjmg.py  # scraper PJe TJMG (ViewState JSF)
│   ├── fontes-cache/                  # cache HTTP das fontes
│   ├── consolidado/                   # CSVs de saída (entregáveis finais)
│   └── logs/                          # logs de cada execução
│
├── download/                          # FLUXO 2 — baixar PDFs do PUSH
│   ├── baixar_push_pje.py             # orquestrador Selenium
│   ├── pje_verificacao.py             # verifica conteúdo PDF (fix bug cache PJe)
│   ├── README.md                      # doc em blocos lógicos
│   └── _analise-erros/                # espaço para investigações futuras
│
├── cadastro/                          # FLUXO 3 — cadastrar CNJ no PUSH
│   ├── incluir_push.py                # orquestrador Playwright
│   ├── mapear_paginas_push.py         # pré-mapeia paginação do PUSH (JSON)
│   ├── README.md                      # doc em blocos lógicos
│   ├── _analise-erros/                # screenshots de falhas
│   └── _mapa/                         # JSONs de mapeamento
│
├── common/                            # Helpers compartilhados
│   ├── config.py                      # SETTINGS dataclass via env
│   ├── cnj.py                         # regex CNJ, validador, slug
│   ├── paths.py                       # processos_dir, quarentena_dir, safe_move
│   ├── logger.py                      # JobLogger (JSONL + REGISTRO.md)
│   ├── browser.py                     # dispatcher local vs remoto CDP
│   ├── cdp.py                         # chrome_debug_vivo, cdp_url
│   ├── pdf.py                         # pdf_valido, extrair_texto, cnj_no_pdf
│   ├── janela.py                      # dentro_janela_tjmg (13h–19h)
│   ├── pje_session.py                 # sessao_ativa, salvar_diagnostico
│   ├── richfaces.py                   # setar_select_jsf, escapar_id
│   └── download.py                    # clicar_e_salvar_download (fallback nova aba)
│
├── renomear/                          # Utilitário pendente
│   └── renomear_cidades.py.TODO       # normalizar nomes de comarca
│
├── _docs/                             # Documentação transversal
│   ├── DIAGRAMA-FLUXO.md              # desenho ASCII do pipeline
│   ├── INDICE-ARQUIVOS.md             # índice completo com descrição
│   └── HISTORICO.md                   # log cronológico de mudanças
│
├── _sessoes/                          # Sessões salvas (transcrição dos pedidos)
│   └── SESSAO-2026-04-19-unificacao-fluxos.md
│
└── _logs/                             # Saída do relatório diário 21h
    └── relatorio-YYYY-MM-DD.md
```

---

## Ordem padrão de trabalho

```
Descoberta (Mac, 21h automático)
        │ gera 3 CSVs
        ▼
Triagem manual do Dr. Jesus
  ├─ PERITO_CONFIRMADO  → alimenta fluxos 2 e 3
  ├─ INDETERMINADO      → Dr. Jesus decide caso a caso
  └─ DESCARTE_PARTE     → não toca (ele é parte, não perito)
        │
        ▼
Download (Windows/Parallels, janela 13–19h TJMG)
        │ PDFs em ~/Desktop/processos-pje-windows/
        ▼
Cadastro no PUSH (Mac, Playwright)
        │
        ▼
Intimações chegam no painel PJe automaticamente
```

---

## O que está funcionando hoje (19/abr/2026)

- [x] `config_pje.py` centralizado (fonte única de URLs/paths/CPF)
- [x] `filtro_perito.py` classifica PERITO / PARTE / INDETERMINADO via `auxiliaresDaJustica` + blacklist
- [x] Fix loop infinito `baixar_push_pje.py` — `_DEDUP_INDEX` persistente em `_downloads_feitos.json`
- [x] READMEs blocos lógicos nos 3 fluxos (descoberta, download, cadastro)
- [x] Skill `/novo-fluxo` + hook PostToolUse Write
- [x] Relatório diário 21h (`_logs/relatorio-YYYY-MM-DD.md`)
- [x] Bot Telegram comando `/processos` (ativa após reiniciar bot)
- [x] Symlinks preservando paths antigos (nada deletado)

---

## Pendências (necessitam ação do Dr. Jesus)

- [ ] Popular `descoberta/blacklist_manual.txt` com CNJs copiados da Consulta Pública TJMG
- [ ] `launchctl load` do plist do relatório diário 21h
- [ ] Reiniciar bot Telegram para registrar comando `/processos`
- [ ] Criar `~/.credenciais-cnj.json` com senha PJe (para AJ/AJG com login)
- [ ] Reativar fonte TRF6 em `descobrir_processos.py` (precisa DevTools — hoje retorna CNJs aleatórios)
- [ ] Decidir motor de busca semântica (local / Supabase / keywords)
- [ ] Rodar descoberta pós-blacklist e validar 3 CSVs
- [ ] Testar download com `--limite 3` para confirmar fix dedup

---

## Commands rápidos

```bash
# 1. Descoberta (Mac, rápido)
cd "~/Desktop/STEMMIA Dexter/src/pje/descoberta" && python3 descobrir_processos.py --sem-browser

# 2. Descoberta com AJ/AJG (Mac, precisa Chrome 9223 logado)
python3 descobrir_processos.py --com-browser

# 3. Download (Windows/Parallels, janela 13-19h)
python baixar_push_pje.py --limite 3          # teste
python baixar_push_pje.py                     # tudo
python baixar_push_pje.py --retry             # só os que falharam

# 4. Cadastro PUSH (Mac)
cd "~/Desktop/STEMMIA Dexter/src/pje/cadastro"
python3 incluir_push.py --dry-run             # ensaio
python3 incluir_push.py                       # pra valer
python3 incluir_push.py --descobrir           # quando PJe muda layout

# 5. Relatório diário manual
python3 ~/stemmia-forense/automacoes/relatorio_pje_diario.py
```

---

## Troubleshooting

| Sintoma | Causa provável | Solução |
|---|---|---|
| `ViewState não encontrado` na descoberta | PJe mudou form JSF | Atualizar regex em `fontes/consulta_publica_tjmg.py` |
| Download baixa mesmo CNJ 7x em loop | Dedup antigo falhou | Verificar se `_downloads_feitos.json` existe na pasta de download |
| `PDF conteúdo divergente` → `_invalidos/` | Bug cache PJe (esperado) | Abrir PDF em quarentena, ver qual CNJ veio trocado, reprocessar |
| Chrome não conecta porta 9223 | Lock file preso | `rm ~/Desktop/chrome-pje-profile/Singleton*` |
| `Timeout esperando login 5min` | Certificado A3 não inserido | Rodar de novo, inserir cert a tempo |
| Duplicatas marcadas como erro no cadastro | Normal | Processo já está no PUSH. Não é falha. |
| Fora da janela TJMG 13-19h | PJe instável fora desse horário | Esperar ou usar `--forcar-horario` / `--ignorar-janela` |

---

## Contatos/paths importantes

- Plano aprovado da unificação: `~/.claude/plans/binary-gliding-pine.md`
- Sessão 19/abr/2026: `src/pje/_sessoes/SESSAO-2026-04-19-unificacao-fluxos.md`
- Log estruturado de erros: `src/pje/_logs/erros_fluxo.jsonl`
- Diário do projeto: `~/Desktop/DIARIO-PROJETOS.md`
- Índice geral do sistema: `~/Desktop/ANALISADOR FINAL/Analisa Processual Completa/07-metodos/00-INDICE-GERAL.md`
- Bot Telegram: `@stemmiapericia_bot` (chat_id `8397602236`)
- PDFs baixados (Windows): `~/Desktop/processos-pje-windows/`
- Pastas dos processos (Mac): `~/Desktop/ANALISADOR FINAL/processos/`

---

## Qualidade de código (ruff + pytest + pre-commit)

Configuração em `pyproject.toml` (ruff + pytest) e `.pre-commit-config.yaml` (hooks).

**Rodar linter:**
```bash
cd "~/Desktop/STEMMIA Dexter/src/pje"
python3 -m ruff check .
python3 -m ruff check . --fix   # aplica correcoes automaticas
```

**Rodar testes smoke (< 1s, 4 testes):**
```bash
python3 -m pytest tests/ -v
```

**Ativar pre-commit (opcional, por decisao do Dr. Jesus nao esta instalado):**
```bash
pip install pre-commit
pre-commit install
```
Depois disso, cada `git commit` roda ruff + pytest automaticamente.

---

Gerado em 2026-04-19. Rever a cada mudança estrutural de pasta ou fluxo.
