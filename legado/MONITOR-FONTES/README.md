# MONITOR-FONTES

Sistema que consulta automaticamente todos os lugares onde Dr. Jesus recebe
citações, intimações e nomeações como perito médico judicial, consolida numa
lista única (deduplicada, em ordem cronológica) e avisa no Telegram quando
aparece algo novo.

---

## Fontes monitoradas

| # | Sistema | URL | Automação | Pré-requisito |
|---|---------|-----|-----------|---------------|
| 1 | AJ TJMG | https://aj.tjmg.jus.br | cron (Playwright) | Chrome 9223 logado |
| 2 | AJG Justiça Federal | https://ajg.cjf.jus.br | cron (Playwright) | Chrome 9223 logado |
| 3 | DJEN / Comunica PJe | https://comunica.pje.jus.br | cron (API) | — |
| 4 | Domicílio Judicial Eletrônico | https://domicilio-eletronico.pdpj.jus.br | cron (IMAP) | credenciais IMAP |
| 5 | DataJud CNJ | API pública | cron (API) | — |
| 6 | PJe TJMG Painel | https://pje.tjmg.jus.br | **manual** (Windows+VidaaS) | rotina 2x/semana |

---

## Estrutura de pastas

```
MONITOR-FONTES/
├── README.md                              ← este arquivo (ler primeiro)
├── scripts/
│   ├── orquestrador.py                    ← roda todas as fontes em sequência
│   ├── consolidador.py                    ← dedup por CNJ + ordem cronológica
│   ├── alerta_telegram.py                 ← diff e envio Telegram
│   ├── gerar_dashboard.py                 ← monta dashboard HTML
│   ├── abrir_chrome_debug.command         ← duplo-click: abre Chrome 9223
│   ├── fixtures/                          ← respostas reais p/ testes
│   ├── test_orquestrador.py
│   ├── test_consolidador.py
│   └── test_alerta.py
├── dados/
│   ├── processos-consolidados.json        ← LISTA MESTRE (lê isso!)
│   ├── processos-consolidados.csv         ← mesma coisa em CSV
│   ├── consolidado-YYYY-MM-DD.json        ← snapshot diário para diff
│   ├── historico/YYYY-MM-DD.json          ← resultado cru do orquestrador
│   └── por-fonte/                         ← resultado cru de cada fonte
│       ├── aj.json
│       ├── ajg.json
│       ├── djen.json
│       ├── domicilio.json
│       └── datajud.json
├── logs/
│   ├── orquestrador-YYYY-MM-DD.log
│   ├── launchd-stdout.log
│   └── launchd-stderr.log
├── docs/
│   ├── COMO-RODAR.md                      ← guia de execução manual
│   ├── ROTINA-PJE-MANUAL.md               ← rotina Windows 2x/semana
│   └── FONTES-E-URLS.md                   ← URLs, auth, APIs
├── dashboard/
│   ├── index.html                         ← abre no browser
│   └── assets/
│       └── style.css
└── config/
    ├── credenciais.env.exemplo            ← modelo (real em ~/.stemmia/)
    └── launchd/
        └── com.stemmia.monitor-fontes.plist
```

**Regra:** 1 pasta = 1 tipo de arquivo. Nunca misturar script com dado com log.

---

## Como rodar (manual)

1. Abrir Chrome debug: duplo-click em `scripts/abrir_chrome_debug.command`
2. Logar em AJ TJMG e AJG (abas separadas)
3. No Terminal: `python3 ~/Desktop/MONITOR-FONTES/scripts/orquestrador.py`
4. Ver resultado em `dados/processos-consolidados.json`
5. Abrir `dashboard/index.html` no browser

Detalhes em `docs/COMO-RODAR.md`.

---

## Como funciona o cron

launchd roda `scripts/orquestrador.py` todo dia às **7h**. Plist em
`config/launchd/com.stemmia.monitor-fontes.plist` (symlink em `~/Library/LaunchAgents/`).

Se o Chrome estiver deslogado em AJ/AJG, o script detecta e **envia lembrete no
Telegram** em vez de falhar silencioso.

---

## Arquivos principais (ordem de importância)

1. `dados/processos-consolidados.json` — **LISTA MESTRE**. CNJs únicos, ordenados
   por data desc. Cada entrada tem `{cnj, data_mais_recente, fontes[], detalhes[]}`.
2. `dashboard/index.html` — visual.
3. `logs/orquestrador-YYYY-MM-DD.log` — se algo der errado, olhar aqui.
4. `dados/por-fonte/*.json` — resultado bruto, 1 arquivo por fonte.

---

## Pré-requisitos

```bash
pip3 install playwright imapclient requests python-dotenv beautifulsoup4
python3 -m playwright install chromium
```

**Credenciais IMAP** (para Domicílio Eletrônico) em `~/.stemmia/credenciais.env`:
```
TELEGRAM_BOT_TOKEN=...
IMAP_HOST=...
IMAP_USER=perito@drjesus.com.br
IMAP_PASS=...
```
(arquivo em `.gitignore`, NUNCA commitar)

---

## Troubleshooting

| Sintoma | Causa provável | Solução |
|---------|----------------|---------|
| AJ/AJG retornam 0 itens | Chrome deslogado | Rodar `abrir_chrome_debug.command` e logar |
| Porta 9223 não responde | Chrome debug não iniciou | Matar Chrome + abrir de novo |
| Domicílio retorna 0 | IMAP sem credenciais | Preencher `~/.stemmia/credenciais.env` |
| Telegram não envia | Token ausente | Preencher `TELEGRAM_BOT_TOKEN` |
| `playwright` não achado | Não instalado | `pip3 install playwright && python3 -m playwright install chromium` |

---

## Última atualização

2026-04-17 — Criação inicial (plano em `~/.claude/plans/monitor-fontes-intimacoes.md`).
