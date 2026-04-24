# Scripts mapeados — FLUXOS 04 e 05 (Modelos/Laudos e Honorários)

## Motor central

| Caminho | Função | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/cowork/05-AUTOMACOES/scripts/aplicar_template.py` | **Motor oficial.** v0.2.0, stdlib only. Substitui `{{path.subpath}}`, `{{#lista:}}`, `{{#se:}}`, `{{#se-nao:}}`. Lê FICHA.json + TEMPLATE.md → MD preenchido | FUNCIONA |

## Orquestrador

| Caminho | Função | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/cowork/05-AUTOMACOES/orquestrador/orquestrador.py` | Roteia FICHA para template certo | FUNCIONA |
| `.../orquestrador/regras_classificacao.json` | Regras de roteamento | FUNCIONA |

## Geração de petição

| Caminho | Função | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/src/peticoes/gerar_peticao.py` | Gera petição a partir de FICHA | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/src/peticoes/laudo_pipeline.py` | Pipeline laudo FICHA → laudo.md | DUVIDOSO (cópia em `_arquivo/Open/analisador-final/scripts/`) |

## Honorários — consulta

| Caminho | Função | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/src/honorarios/pesquisar_honorarios.py` | Busca decisões TJMG por filtros | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/FERRAMENTAS/pesquisador-honorarios/pesquisar_honorarios.py` | Duplicata | DUVIDOSO |
| `/Users/jesus/Desktop/STEMMIA Dexter/FERRAMENTAS/pesquisador-honorarios/dados/honorarios.db` | SQLite honorários TJMG | DADOS |
| `/Users/jesus/Desktop/STEMMIA Dexter/_arquivo/PESQUISADOR-HONORARIOS/dados/importar_fichas.py` | Importador legado | LEGADO |

## Honorários — Taiobeiras (base histórica AJG)

| Caminho | Função | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/taiobeiras-status/taiobeiras_status.py` | Status dos 6 casos Taiobeiras R$ 612 | FUNCIONA |

## Verificador de proposta/petição

| Caminho | Função | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/verificadores/verificador_peticao_pdf.py` | Verifica petição emitida em PDF | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/agents/orquestradores/orquestrador-verificacao-proposta.md` | Orquestrador MD de verificação | AGENTE |

## Templates — laudos

| Caminho | Classe | Status |
|---|---|---|
| `/Users/jesus/Desktop/_MESA/10-PERICIA/templates-reaproveitaveis/INDEX.md` | Catálogo | PRONTO |
| `.../templates-reaproveitaveis/formatos-laudo/acidente-trabalho.md` | AT | PRONTO |
| `.../templates-reaproveitaveis/formatos-laudo/securitario-invalidez.md` | Securitário invalidez | PRONTO |
| `.../templates-reaproveitaveis/exames-fisicos/coluna-lombar.md` | Bloco exame lombar | PRONTO |
| `.../templates-reaproveitaveis/exames-fisicos/joelho.md` | Bloco exame joelho | PRONTO |
| `/Users/jesus/Desktop/STEMMIA Dexter/cowork/02-BIBLIOTECA/laudos/` | Só symlinks | **VAZIO** |

## Templates — propostas de honorários

| Caminho | Classe | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/cowork/02-BIBLIOTECA/peticoes/proposta-honorarios/TEMPLATE.md` | Genérico | PRONTO |
| `.../proposta-honorarios/placeholders.json` | Schema | PRONTO |
| `.../proposta-honorarios/civel-dano-pessoal/INVENTADO-NAO-USAR-TEMPLATE.md` | Cível dano pessoal (inventado) | **NÃO USAR** |
| erro-medico/ | Erro médico | **FALTA** |
| securitario/ | Securitário | **FALTA** |
| previdenciario/ | Previdenciário | **FALTA** |
| trabalhista/ | Trabalhista | **FALTA** |
| `.../peticoes/aceite/TEMPLATE.md` | Aceite simples | PRONTO |
| `.../peticoes/aceite/TEMPLATE-condicionado.md` | Aceite condicionado | PRONTO |
| `.../peticoes/escusa/INVENTADO-NAO-USAR-TEMPLATE.md` | Escusa (inventado) | **NÃO USAR** |

## Tabelas oficiais AJG (dados, não scripts)

Raiz: `/Users/jesus/Desktop/STEMMIA Dexter/banco-de-dados/Banco-Transversal/Honorarios-Periciais/Tabelas-Oficiais/`

- TJMG Portaria 6180/2023, 6607/2024, **7231/2025 (vigente)**, Tabela I DJe 21/06/2024
- CJF Res 305/2014 (JF/TRF6)
- CSJT Res 66/2010 (trabalhista)
- CNJ Res 424/2021 (cadastro peritos)
- TRF6 por comarca: Muriaé, BH, JEF 3821, JEF 3806, JEF 3800

## Base histórica Taiobeiras AJG

| Caminho | Conteúdo |
|---|---|
| `.../Honorarios-Periciais/Casos-Reais/Norte-Mineiro/taiobeiras-vara-unica-consolidado-0680.md` | 6 processos R$ 612, 2021-2025 |
| `.../taiobeiras-vara-unica-consolidado-0680.FICHA.json` | FICHA consolidada |
| `/Users/jesus/Desktop/_MESA/10-PERICIA/aceites-taiobeiras-22abr/_README.md` | Contexto operacional |
| `/Users/jesus/Desktop/STEMMIA Dexter/memoria/base-conhecimento/honorarios.md` | Doc consolidada |

## Agentes MD de laudo/petição

| Caminho | Papel |
|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/agents/clusters/geral/redator-laudo.md` | Redator de laudo |
| `/Users/jesus/Desktop/STEMMIA Dexter/agents/clusters/geral/revisor-laudo.md` | Revisor de laudo |
| `.../agents/clusters/redacao/gerador-roteiro-pericial.md` | Gera roteiro HTML exame presencial |
| `.../agents/clusters/redacao/padronizador-estilo.md` | Consulta PERFIL-ESTILO (hoje desconectado) |

## Perfil de Estilo

| Caminho | Estado |
|---|---|
| iCloud `Stemmia/PERÍCIA/PADRONIZADOR PETIÇÕES/PERFIL-ESTILO.json` | 88 KB, analisou 68 petições. **Não tem cópia local.** Não está plugado em nenhum script. |

## Lacunas críticas

- 4 templates de proposta por classe **faltam**.
- Pasta `cowork/02-BIBLIOTECA/laudos/` **vazia** (só symlinks).
- `scorer-complexidade.py` mencionado no pipeline — **não existe**.
- Agente `cfm-buscador` (para erro-médico) — **não existe**.
- PERFIL-ESTILO.json — **não está local**.
- `pesquisar_honorarios.py` tem 2 cópias — decidir qual é oficial.
- `laudo_pipeline.py` tem 2 cópias — decidir qual é oficial.
