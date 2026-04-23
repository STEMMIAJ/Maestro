---
titulo: Journals — periódicos revisados por pares
tipo: readme_fonte
versao: 0.1
status: ativo
ultima_atualizacao: 2026-04-23
evidence_level_padrao: academico
---

# 12_sources/journals

Periódicos revisados por pares (peer-reviewed). Base de referência para afirmações técnicas. `evidence_level: academico` quando houver DOI + indexação reconhecida.

## Saúde / Medicina

- **JAMA** — Journal of the American Medical Association. https://jamanetwork.com/journals/jama
- **NEJM** — New England Journal of Medicine. https://www.nejm.org/
- **The Lancet** — https://www.thelancet.com/
- **BMJ** — British Medical Journal. https://www.bmj.com/
- **Cochrane Library** — revisões sistemáticas. https://www.cochranelibrary.com/
- **Revista Brasileira de Medicina Legal** — ABML (quando disponível).
- **Cadernos de Saúde Pública (ENSP/Fiocruz)** — https://cadernos.ensp.fiocruz.br/

## IA / CS

- **JMLR** — Journal of Machine Learning Research. https://www.jmlr.org/ (open access)
- **TMLR** — Transactions on Machine Learning Research. https://jmlr.org/tmlr/
- **CACM** — Communications of the ACM. https://cacm.acm.org/
- **IEEE TPAMI** — Transactions on Pattern Analysis and Machine Intelligence.
- **arXiv** — https://arxiv.org/ (pré-print, `evidence_level: academico_preprint` até peer review).

## Conferências com proceedings peer-reviewed (equivalente a journal)

- **NeurIPS, ICML, ICLR** — IA/ML.
- **ACL, EMNLP, NAACL** — NLP.
- **SOSP, OSDI, NSDI** — sistemas.
- **USENIX Security, IEEE S&P** — segurança.

## Regras

- Arquivo por paper/artigo: `<ano>_<primeiro_autor>_<slug>.md`.
- Frontmatter: `titulo`, `autores`, `ano`, `periodico`, `doi`, `url`, `bloco`, `evidence_level`, `status_leitura`.
- DOI é obrigatório quando existir. Sem DOI → `evidence_level: academico_preprint` ou rebaixar.
- Acesso via PubMed (MCP disponível) ou Crossref.

## Uso operacional

- Pergunta médica → PubMed MCP + buscador-academico em paralelo (CLAUDE.md global).
- Citação em laudo só com periódico indexado + DOI ativo.

## TODO

- Definir lista de journals "aceitos" para laudo vs "aceitos" para nota de estudo.
- Catalogar PMIDs já lidos e relevantes.
