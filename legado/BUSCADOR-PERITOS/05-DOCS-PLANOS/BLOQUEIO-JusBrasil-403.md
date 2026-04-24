# Bloqueio de coleta — Decisoes TJMG honorarios periciais interior MG

Data: 2026-04-20
Executor: Claude Opus 4.7
Meta inicial: 15-25 decisoes Zona Mata Sul + Triangulo/Alto Paranaiba + Norte Mineiro + Outros

## Resultado

Coletado efetivamente: **1 caso PARCIAL** (Montes Claros 2020, perícia grafotécnica, R$ 660).
Meta nao atingida.

## Causa raiz

Fontes abertas indexaveis por WebSearch/WebFetch NAO retornam decisoes individuais com CNJ+valor+PDF. Todas as tentativas retornaram apenas **regulamentacao geral** (Portaria TJMG 6607/PR/2024 com piso R$ 585,66 para pericia medica em AJG, Res. CJF 575/2019, tabelas).

Barreiras tecnicas:
1. **Jusbrasil**: HTTP 403 no WebFetch em qualquer `/diarios/` ou `/jurisprudencia/` (WAF anti-bot).
2. **TJMG jurisprudencia** (`www5.tjmg.jus.br/jurisprudencia/`): retorna 401 sem sessao JSF; busca via GET nao funciona.
3. **DJE TJMG** (`dje.tjmg.jus.br`): F5 WAF bloqueia acesso sem JS/cookies.
4. **Indexacao Google/Bing**: numeros de processo aparecem mascarados (`XXXXX-XX.XXXX.8.13.XXXX`) — Jusbrasil protege CNJ completo.
5. **Escavador**: idem, exige login/API-key.

## O que existe valido publicamente (base normativa)

- **Portaria TJMG 6607/PR/2024** (http://www8.tjmg.jus.br/institucional/at/pdf/po66072024.pdf) — tabela vigente.
- **Portaria TJMG 6180/PR/2023** (http://www8.tjmg.jus.br/institucional/at/pdf/po61802023.pdf) — tabela anterior.
- **Portaria TJMG 7231/2025** (http://www8.tjmg.jus.br/institucional/at/pdf/po72312025.pdf) — tabela 2025+.
- **Res. CJF 575/2019** (federal, TRF6).
- **Tema 64 IRDR TJMG** — competencia para cobranca contra Estado MG.

Esses PDFs normativos ja deveriam estar em `Tabelas-Oficiais/` — separado deste diretorio.

## Caminho alternativo (proxima sessao)

Para cumprir a meta 15-25 casos sao necessarias UMA das opcoes:

1. **Playwright com browser visivel + sessao** no TJMG jurisprudencia consulta livre (usuario tem sessao ativa no Chrome/Parallels).
2. **API Escavador paga** (`escavador-mcp`) — requer chave.
3. **Download manual de 20 DJMGs** por pagina PJe com cookies e extracao automatica.
4. **Consulta PJe direta** via certificado A3 no Parallels Windows (funciona desde 13/abr/2026, ref `project_download_pje_139.md`).

## Recomendacao

Nao tentar mais busca aberta. Enquadrar como **Fase 0** concluida com 1 caso PARCIAL registrado + guia de bloqueio. Fase 1 depende de decisao do Dr. Jesus sobre qual caminho alternativo seguir.

## Arquivos criados nesta sessao

- `Casos-Reais/Norte-Mineiro/tjmg-montes-claros-grafotecnica-2020-djmg0309.md`
- `Casos-Reais/Norte-Mineiro/tjmg-montes-claros-grafotecnica-2020-djmg0309.FICHA.json`
- `Casos-Reais/_BLOQUEIO-COLETA-20260420.md` (este arquivo)

## Paths vazios (aguardando alternativa)

- `Casos-Reais/Zona-Mata-Sul/` (0 casos)
- `Casos-Reais/Triangulo-Alto-Paranaiba/` (0 casos)
- `Casos-Reais/Outros-regiao-MG/` (0 casos)
- `Casos-Reais/Norte-Mineiro/` (1 caso PARCIAL)
