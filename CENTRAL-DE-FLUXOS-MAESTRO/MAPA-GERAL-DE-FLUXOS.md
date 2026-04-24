# Mapa Geral de Fluxos

Marcar com `URGENTE` ao lado do fluxo mais crítico para a próxima sessão.

## Tabela principal

| # | Fluxo | Objetivo | Entrada | Saída | Scripts principais | Status |
|---|---|---|---|---|---|---|
| 01 | Captura de processos | Saber quais processos caíram para você | Login AJ TJMG / AJG CJF / PJe / DJEN | Lista de CNJs novos | `consultar_aj.py`, `consultar_ajg.py`, `sincronizar_aj_pje.py`, `djen.py`, `comunica_pje.py`, `descobrir_processos.py` | PARCIAL (AJ/AJG OK; PJe direto falta) |
| 02 | Download de PDFs | Baixar todas as peças de um processo | CNJ + PUSH PJe marcado | PDFs na pasta do processo | `baixar_direto_selenium.py`, `CLICAR_AQUI_BAIXAR_PJE.command`, `baixar_push_pje.py`, `faltam_baixar.py` | PRONTO (Windows/Parallels) |
| 03 | Análise de processos | Gerar FICHA.json + resumo legível | PDFs baixados + OCR | FICHA.json + ANALISE.md + RESUMO-3-LINHAS.md | `pipeline_analise.py`, `extrair_partes.py`, `resumir_fatos.py`, `extrair_quesitos.py`, `classificar_acao.py`, `scanner_processos.py` | RASCUNHO (scripts existem, mas OCR em lote **FALTA**) |
| 04 | Modelos e laudos | Montar laudo a partir de FICHA + exame | FICHA.json + notas do exame + quesitos | LAUDO.md + PDF timbrado | `aplicar_template.py`, `laudo_pipeline.py`, templates em `_MESA/10-PERICIA/templates-reaproveitaveis/`, agente `redator-laudo` | PARCIAL (só 2 formatos prontos: AT + securitário-invalidez) |
| 05 | Honorários | Proposta (parte paga) **OU** consulta tabela (AJG) | FICHA.json + classe processual | Petição proposta.md/pdf **OU** valor AJG confirmado | `aplicar_template.py` + `TEMPLATE.md` (proposta), `pesquisar_honorarios.py`, base Taiobeiras R$612 | RASCUNHO (só template cível-dano-pessoal real; erro-médico/securitário/previdenciário/trabalhista **FALTAM**) |
| 06 | Jurisprudência e sentenças | Buscar precedentes e laudos elogiados | CID / comarca / tema | Base SQLite `jurisprudencia.db` + HTMLs | `coletor_tjmg_jurisprudencia.py`, `baixar_tjmg_v3.py`, `datajud_api.py`, MCP `brlaw_mcp_server`, agente `orq-jurisprudencia` | PRONTO (TJMG com captcha manual 1ª vez; DataJud e MCP livres) |
| 07 | Memória e GitHub | Versionar fluxos sem vazar segredo | Arquivos .md e scripts | Repo STEMMIAJ/Maestro | Hook "salva no github" (auto) | **A AUDITAR** (status duvidoso, pushes sem revisão) |

## Legenda de status

- **PRONTO** = roda hoje, sem intervenção manual além do esperado.
- **PARCIAL** = roda parte do caminho, resto manual.
- **RASCUNHO** = script/template existe mas não fecha o fluxo todo.
- **FALTANDO** = pedaço crítico ausente.
- **A AUDITAR** = funciona mas ninguém sabe se está correto.

## Marque URGENTE aqui

Escreva `URGENTE` ao lado do fluxo mais crítico da semana:

- [ ] FLUXO 01 — Captura de processos
- [ ] FLUXO 02 — Download de PDFs
- [ ] FLUXO 03 — Análise de processos
- [ ] FLUXO 04 — Modelos e laudos
- [ ] FLUXO 05 — Honorários
- [ ] FLUXO 06 — Jurisprudência e sentenças
- [ ] FLUXO 07 — Memória e GitHub
