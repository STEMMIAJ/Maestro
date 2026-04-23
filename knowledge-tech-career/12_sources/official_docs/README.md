---
titulo: Official Docs — fontes oficiais
tipo: readme_fonte
versao: 0.1
status: ativo
ultima_atualizacao: 2026-04-23
evidence_level_padrao: oficial
---

# 12_sources/official_docs

Documentação oficial de linguagens, plataformas, órgãos reguladores. Confiança máxima (`evidence_level: oficial`) quando o domínio e o autor batem com a lista canônica.

## Canônicos por bloco

### Tecnologia
- **Python** — https://docs.python.org/3/
- **MDN Web Docs** — https://developer.mozilla.org/ (HTML/CSS/JS/Web APIs)
- **Django** — https://docs.djangoproject.com/
- **FastAPI** — https://fastapi.tiangolo.com/
- **Linux man pages** — `man`, https://man7.org/linux/man-pages/
- **PostgreSQL** — https://www.postgresql.org/docs/
- **Git** — https://git-scm.com/docs
- **Anthropic API** — https://docs.anthropic.com/
- **OpenAI API** — https://platform.openai.com/docs

### Saúde / Perícia BR
- **CNJ** — https://www.cnj.jus.br/
- **CFM** — https://portal.cfm.org.br/ (resoluções, pareceres)
- **CRM-MG** — https://crmmg.org.br/
- **ANVISA** — https://www.gov.br/anvisa/pt-br
- **Ministério da Saúde** — https://www.gov.br/saude/pt-br
- **DATASUS / TABNET** — https://datasus.saude.gov.br/
- **INSS / e-Social** — https://www.gov.br/inss/pt-br
- **DataJud CNJ** — ver `~/Desktop/STEMMIA Dexter/DOCS/datajud/DATAJUD-GUIA.md`

### Direito BR
- **Planalto (leis)** — https://www.planalto.gov.br/
- **STF** — https://portal.stf.jus.br/
- **STJ** — https://www.stj.jus.br/
- **TRFs, TJs, TRTs** — por regional (catalogar conforme uso)

## Regras de catalogação

- Cada item vira `<slug>.md` com frontmatter: `titulo`, `autor`, `url`, `evidence_level: oficial`, `ultima_verificacao`.
- URL oficial obrigatória no corpo; cópia local (PDF) opcional.
- Pipeline `source_validation_pipeline_spec.md` re-checa trimestralmente.
- Mudança de URL (redirect permanente) → atualizar, versionar no Git, registrar em `13_reports/`.

## TODO

- Criar `_authors.yaml` com domínios oficiais para auto-classificação.
- Popular arquivos individuais conforme uso real — não criar 30 stubs vazios.
