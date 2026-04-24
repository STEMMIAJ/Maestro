# Buscador de Oportunidades para Perito

**Consolidado em:** 2026-04-20
**Objetivo:** mapear oportunidades periciais (nomeações, vagas, déficit) em comarcas num raio de 200km de Governador Valadares/MG usando scraping (JusBrasil) + integração DataJud API.

## Estrutura

### 01-CODIGO-ATIVO/
Código fonte atual. Origem: `~/Library/Mobile Documents/com~apple~CloudDocs/Stemmia/Projetos - Plan Mode/buscador-peritos/`

Principais arquivos:
- `main.py` — CLI (--buscar, --dashboard, --servidor, --status, --limpar, --auto)
- `config.py` — 32 comarcas MG (200km de GV), termos, porta 8889, recência 12 meses
- `buscadores/jusbrasil.py` — Playwright chromium, 2 fases (DJMG + por comarca), lida Cloudflare
- `db.py` — SQLite (oportunidades + buscas)
- `dashboard.py` — HTTP server localhost:8889 com filtros
- `notifier.py` — osascript + afplay
- `data/oportunidades.db` — 168KB, última busca 24/02/2026

Status: última execução bem-sucedida 24/02/2026. Launchd com erros desde 20/03.

### 02-INTEGRACAO-DATAJUD/
Integração DataJud CNJ (planejada, parcialmente implementada). Origem: `~/stemmia-forense/src/pje/monitor-publicacoes/`

- `datajud_client.py` — cliente unificado para api-publica.datajud.cnj.jus.br
- `datajud_api_stemmia.py` — wrapper que lê STATUS-PROCESSOS.json
- `comunica_pje.py` — monitor CNJ Comunica PJe (3 camadas: CPF+TJMG, DataJud recente, varredura semanal)
- `monitor_publicacoes.py` — orquestrador 3 fontes (DataJud + DJe TJMG + Comunica)
- `dje_tjmg.py` — scraper DJe MG
- `datajud_enriquecido.json` — 8 CNJs TJMG com metadados
- `PARAMETROS_DATAJUD.md` — documentação da API

### 03-OUTPUTS-RADAR/
Relatórios e snapshots. Origem: `~/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Radar/`

- `scanner.sh`, `gerar-relatorio*.py`, `resumo-telegram.sh`
- `semanal/Semana-10-2026.html` (1.6 MB)
- `diario/2026-03-03.html`
- `dados/snapshot-*.json` (57 snapshots, 02 a 20 mar 2026)
- `logs/launchd_err.log` — erros recentes

Status: parou em 20/03 com erros no launchd.

### 04-BACKUPS-ANTIGOS/
Versões do backup de 19/04/2026 pré-reorganização.

### 05-DOCS-PLANOS/
- `PLANO-monitor-fontes.md` — plano mestre 5 fontes (AJ TJMG, AJG JF, DJEN/Comunica, Domicílio Judicial, DataJud), ainda nenhuma task concluída
- `PESQUISA-JusBrasil-JusIA.md` — 39 matches, pesquisa completa plataformas
- `RANKING-Plataformas.md` — ranking Escavador/JusBrasil PRO/JUDIT/Codilo/Advise
- `BLOQUEIO-JusBrasil-403.md` — JusBrasil bloqueando WebFetch (WAF)

## Pendências
- Reativar launchd (com.stemmia.descoberta-diaria, com.stemmia.monitor-fontes, com.stemmia.monitor-datajud)
- Fix erros recentes em logs/launchd_err.log
- Completar tasks do PLANO-monitor-fontes.md (0/9 concluídas)
- Contornar bloqueio WAF JusBrasil (403)

## Caminhos originais (NÃO movidos — apenas copiados)
Tudo em `01-CODIGO-ATIVO/` continua vivo em `~/Library/Mobile Documents/com~apple~CloudDocs/Stemmia/Projetos - Plan Mode/buscador-peritos/`.
Tudo em `03-OUTPUTS-RADAR/` continua vivo em `~/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Radar/`.
