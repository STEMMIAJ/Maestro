# FONTES DE PROCESSOS — Separadas por exigência de login

**Criado:** 2026-04-29
**Local oficial:** `~/Desktop/STEMMIA Dexter/src/pje/descoberta/docs/FONTES-POR-AUTENTICACAO.md`
**Função:** decidir, em 5 segundos, qual script rodar conforme a fonte exige login VidaaS/certificado ou não.

---

## REGRA DE OURO

- Quer rodar **agora, sem login** → use as fontes do Grupo A.
- Quer pegar **AJ + AJG + painel PJe** → use o Grupo B (precisa estar logado).
- Quer **descobrir tudo de uma vez** → `descobrir_processos.py` mistura A + B (com flag `--com-browser` quando ativa B).

---

## GRUPO A — SEM LOGIN (fontes públicas)

Rodam direto, sem certificado, sem VidaaS, sem Safari logado. Usam só `requests`/`urllib`.

| # | Fonte | URL base | Script | Função no script | Output |
|---|-------|----------|--------|------------------|--------|
| 1 | **DJe TJMG** (Diário Oficial Eletrônico) | `https://www.tjmg.jus.br/portal-tjmg/` (HTML diário) | `descobrir_processos.py` | `fonte_dje_tjmg(dias=N)` (linhas 160–199) | CNJs perto do nome do perito |
| 2 | **DataJud CNJ** (API pública) | `https://api-publica.datajud.cnj.jus.br/api_publica_<tribunal>/_search` | `descobrir_processos.py` | `consultar_datajud_cnj(cnj, tribunal)` (linhas 206–279) | metadados (classe, OJ, grau, movimentos) |
| 3 | **PJe Consulta Pública TJMG** | `https://pje.tjmg.jus.br/pje/ConsultaPublica/listView.seam` | `descobrir_processos.py` | `fonte_pje_consulta_publica()` (linhas 286–378) | CNJs por CPF do perito |
| 4 | **Portal TJMG Unificado** (PJe + Themis + Projudi) | `https://www.tjmg.jus.br/portal-tjmg/processos/andamento-processual/` | `descobrir_processos.py` | `fonte_portal_tjmg()` (linhas 385–513) | CNJs em sistemas antigos |
| 5 | **PJe TRF6 Consulta Pública** (Federal) | `https://pje1g.trf6.jus.br/consultapublica` + `pje2g.trf6.jus.br` | `descobrir_processos.py` | `fonte_pje_trf6()` (linhas 385–513) | **DESABILITADA** (TODO: retorna CNJs aleatórios) |
| 6 | **DJEN / Comunica PJe** (CNJ) | `https://comunicaapi.pje.jus.br/api/v1/comunicacao` | `descobrir_processos.py` | `fonte_comunica_pje(dias=N)` (linhas 599–695) | intimações filtradas por PERIT/NOMEADO/LAUDO |

### Como rodar Grupo A

```bash
cd "/Users/jesus/Desktop/STEMMIA Dexter/src/pje/descoberta"

# Tudo público (sem browser)
python3 descobrir_processos.py --sem-browser

# Últimos 7 dias do DJe + DJEN
python3 descobrir_processos.py --sem-browser --dias 7

# Pula DataJud (mais rápido, se a API estiver instável)
python3 descobrir_processos.py --sem-browser --skip-datajud
```

**Saídas:** `consolidado/RELATORIO_PROCESSOS_DDMMYYYY.csv` + pastas vazias com `FICHA.json` para cada CNJ novo.

---

## GRUPO B — COM LOGIN (fontes autenticadas)

Exigem login via **VidaaS** (gov.br / certificado A1/A3 / face / código). Cada uma precisa de um browser ativo:

- **Playwright Chromium** (próprio do script, dados em `~/.pje-browser-data`) — para AJ, AJG, download PDFs PJe.
- **Safari já aberto e logado** — para Expedientes, Acervo, Push.
- **Chrome remoto na porta 9223** — alternativa para AJ/AJG no `descobrir_processos.py --com-browser`.

| # | Fonte | URL base | Script | Função no script | Output | Browser |
|---|-------|----------|--------|------------------|--------|---------|
| 7 | **AJ TJMG** (Assistência Judiciária — nomeações estaduais) | `https://aj.tjmg.jus.br/aj/internet/consultarNomeacoes.jsf` | `mapear_aj_ajg_tjmg.py` | `listar_aj(page, situacao)` | nº nomeação, CNJ, unidade, data, dias até aceite, valor, situação | Playwright Chromium |
| 8 | **AJG Federal** (CJF — nomeações federais) | `https://ajg.cjf.jus.br/ajg2/internet/nomeacoes/consultanomeacoes.jsf` | `mapear_aj_ajg_tjmg.py` | `listar_ajg(page, situacao)` | mesma estrutura do AJ | Playwright Chromium |
| 9 | **PJe TJMG — Expedientes** (intimações pendentes) | `https://pje.tjmg.jus.br/pje/Painel/painel_usuario/advogado.seam` (aba Expedientes) | `mapear_expedientes_acervo_tjmg.py` | `mapear_expedientes()` | CSV: CNJ + categoria + comarca | Safari + AppleScript |
| 10 | **PJe TJMG — Acervo** (todos os processos onde sou parte) | mesmo painel, aba Acervo | `mapear_expedientes_acervo_tjmg.py` | `mapear_acervo()` | CSV: CNJ + jurisdição + caixa | Safari + AppleScript |
| 11 | **PJe TJMG — Push** (cadastrados para receber intimação) | `https://pje.tjmg.jus.br/pje/Push/listView.seam` | `mapear_push_tjmg.py` | `mapear_push()` | CSV: CNJ + página + comarca | Safari + AppleScript |
| 12 | **PJe TJMG — Download PDFs** (autos completos) | `https://pje.tjmg.jus.br/pje/Painel/painel_usuario/Usuario.seam` | `mapear_aj_ajg_tjmg.py` | `baixar_pdfs(page, cnjs)` | PDF `autos-completos.pdf` por CNJ | Playwright Chromium |

### Como rodar Grupo B

```bash
cd "/Users/jesus/Desktop/STEMMIA Dexter/src/pje/descoberta"

# AJ + AJG + baixa pendentes (Playwright; abre browser próprio, login VidaaS uma vez por dia)
python3 mapear_aj_ajg_tjmg.py --tudo

# Só listar AJ TJMG pendentes
python3 mapear_aj_ajg_tjmg.py --aj --pendentes --json

# Só listar AJG Federal
python3 mapear_aj_ajg_tjmg.py --ajg --json

# Painel PJe (Safari já logado): expedientes + acervo
python3 mapear_expedientes_acervo_tjmg.py

# Painel PJe (Safari já logado): Push
python3 mapear_push_tjmg.py

# Cruza expedientes + acervo + push (depois dos 3 acima)
python3 cruzar_listas_processos.py
```

**Saídas Grupo B:**
- `output/expedientes_raw.csv`
- `output/acervo_raw.csv`
- `output/push_raw.csv`
- `output/processos_unificados.csv` (gerado por `cruzar_listas_processos.py`)
- `~/stemmia-forense/data/processos/<CNJ>/autos-completos.pdf` (downloads)
- `~/stemmia-forense/data/processos/ultima-sincronizacao.json`

---

## CRUZAMENTO FINAL (mistura Grupo A + Grupo B)

Para gerar a **lista mestre única deduplicada**:

```bash
cd "/Users/jesus/Desktop/STEMMIA Dexter/src/pje/descoberta"

# Espera 2 inputs em ../_input/:
#   nomeacoes-AAAA-MM-DD.md  (AJ + AJG, do mapear_aj_ajg_tjmg.py --json)
#   pje-push-AAAA-MM-DD.md   (Push, do mapear_push_tjmg.py)
python3 cruzar_fontes.py
```

**Saída:** `consolidado/CONSOLIDADO_FONTES_DDMMYYYY.csv` com colunas:
- `cnj`
- `comarca_cod` / `comarca_nome`
- `em_pje` (S/N)
- `em_aj_ajg` (S/N)
- `baixado` (S/N — confere com 3 pastas locais)
- `acao` (`OK_BAIXADO` / `BAIXAR` / `CADASTRAR_PUSH`)

E mais dois TXT prontos para colar no PJe:
- `consolidado/FALTA_BAIXAR_DDMMYYYY.txt`
- `consolidado/FALTA_CADASTRAR_PUSH_DDMMYYYY.txt`

---

## DEPENDÊNCIAS POR GRUPO

| Grupo | Python | Browser | Login | Tempo |
|-------|--------|---------|-------|-------|
| A (público) | stdlib + `requests` | nenhum | nenhum | ~2 min |
| B (autenticado) | stdlib + `playwright` | Chromium próprio **OU** Safari logado | VidaaS (gov.br + face/código/certificado) | ~10 min (1ª vez 15 min com login manual) |

```bash
# Instalar Playwright (Grupo B Chromium)
pip3 install playwright && python3 -m playwright install chromium

# Instalar requests (Grupo A)
pip3 install requests
```

---

## ARQUIVOS DESTE PIPELINE — onde tudo vive

```
~/Desktop/STEMMIA Dexter/src/pje/
├── _input/                              ← inputs colados manualmente
│   ├── nomeacoes-AAAA-MM-DD.md          (AJ + AJG)
│   └── pje-push-AAAA-MM-DD.md           (Push)
└── descoberta/                          ← TUDO FICA AQUI
    ├── docs/
    │   └── FONTES-POR-AUTENTICACAO.md   ← este arquivo
    ├── output/                          ← saídas dos scripts Safari
    │   ├── expedientes_raw.csv
    │   ├── acervo_raw.csv
    │   ├── push_raw.csv
    │   └── processos_unificados.csv
    ├── consolidado/                     ← lista mestre + relatórios
    │   ├── CONSOLIDADO_FONTES_DDMMYYYY.csv
    │   ├── FALTA_BAIXAR_DDMMYYYY.txt
    │   ├── FALTA_CADASTRAR_PUSH_DDMMYYYY.txt
    │   ├── RELATORIO_PROCESSOS_DDMMYYYY.csv
    │   └── NOMEACOES_*.csv
    ├── fontes-cache/                    ← cache HTTP das fontes públicas
    ├── log/                             ← logs por execução
    ├── core/                            ← filtro_perito.py (anti-homônimo)
    ├── fontes/                          ← consulta_publica_tjmg.py
    ├── blacklist_manual.txt             ← CNJs a ignorar
    │
    ├── descobrir_processos.py           [Grupo A + B] orquestrador 6 fontes
    ├── mapear_aj_ajg_tjmg.py            [Grupo B] AJ + AJG + download PDFs
    ├── mapear_expedientes_acervo_tjmg.py [Grupo B] Expedientes + Acervo
    ├── mapear_push_tjmg.py              [Grupo B] PJe Push
    ├── cruzar_listas_processos.py       [união expedientes + acervo + push]
    ├── cruzar_fontes.py                 [união AJ/AJG + Push + baixados locais]
    ├── conferir_nomeacoes.py            [confere lista vs PDFs locais]
    ├── ordenar_nomeacoes.py             [prioridade Taiobeiras→GV→Mantena]
    └── README.md                        [doc do orquestrador, 12 blocos]
```

**PDFs baixados:** `~/stemmia-forense/data/processos/<CNJ>/autos-completos.pdf`

---

## RESUMO PARA AÇÃO HOJE

1. **Sem login (rápido)** → `python3 descobrir_processos.py --sem-browser --dias 7`
2. **Com login (completo)** → `python3 mapear_aj_ajg_tjmg.py --tudo`
3. **Lista mestre** → exportar Push manualmente para `_input/pje-push-DATA.md` + AJ/AJG para `_input/nomeacoes-DATA.md` → `python3 cruzar_fontes.py`

Saída final é sempre `consolidado/CONSOLIDADO_FONTES_DDMMYYYY.csv` — esta é a lista mestre única.
