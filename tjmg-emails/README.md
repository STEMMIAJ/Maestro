# tjmg-emails — Base de contatos das comarcas TJMG

Pasta dedicada ao extrator de emails das 298 sedes do TJMG + consultor por proximidade de Governador Valadares.

## Status atual (2026-04-24)
- ✅ 297/298 sedes com email (99,7%)
- ✅ 1.038 emails únicos (1.172 totais)
- ⚠️ 96 emails inferidos (~8%) — auditoria pendente
- 🔜 Aguardando lista TJMG+JF do Dr. Jesus para próximo passo

## Arquivos

| Arquivo | Descrição |
|---|---|
| `HANDOFF.md` | Estado completo da sessão para retomar |
| `extrator_completo.py` | Lê 1621 PDFs do guia TJMG, extrai contatos (4,1s) |
| `comarcas_proximas_gv.py` | CLI consulta comarcas por raio km de GV |
| `contatos_completo.json` | Base mestre — 1616 entradas (1,1 MB) |
| `output/comarcas_50km.md` | 4 comarcas mais próximas |
| `output/comarcas_100km.md` | 13 comarcas |
| `output/comarcas_200km.md` | 43 comarcas |
| `output/comarcas_100km.csv` | Pronto p/ Excel/mailmerge |

## Schema `contatos_completo.json`
Ver `HANDOFF.md` seção 3.

## Como rodar
```bash
# Re-extrair (precisa dos 1621 PDFs em ~/Desktop/_MESA/30-DOCS/guia-judiciario-TJMG/)
python3 extrator_completo.py

# Consultar
python3 comarcas_proximas_gv.py --raio 100 --formato md --output output/comarcas_100km.md
python3 comarcas_proximas_gv.py --raio 200 --com-email --formato csv
```

## Origem
Projeto pai: `~/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/guia-tjmg-classificador/`
PDFs origem: `~/Desktop/_MESA/30-DOCS/guia-judiciario-TJMG/` (1621 arquivos)
Scraper que gerou os PDFs: `PYTHON-BASE/08-SISTEMAS-COMPLETOS/guia-tjmg-scraper/scraper.py`

## Próximos passos
Ver `HANDOFF.md` seção 6.
