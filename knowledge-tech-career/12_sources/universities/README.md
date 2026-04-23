---
titulo: Universities — cursos abertos e material acadêmico
tipo: readme_fonte
versao: 0.1
status: ativo
ultima_atualizacao: 2026-04-23
evidence_level_padrao: academico
---

# 12_sources/universities

Material acadêmico de universidades com reputação estabelecida. `evidence_level: academico` por padrão.

## Núcleo recomendado

### Internacionais — CS/Eng
- **MIT OpenCourseWare** — https://ocw.mit.edu/ (6.006 Algoritmos, 6.S191 Deep Learning, 18.06 Álgebra Linear)
- **Stanford CS** — https://cs.stanford.edu/ (CS229 ML Andrew Ng, CS224N NLP, CS231N CV)
- **Harvard CS50** — https://cs50.harvard.edu/ (CS50x, CS50p, CS50w)
- **Berkeley CS** — https://www2.eecs.berkeley.edu/Courses/ (CS61A, CS61B, CS188 AI)
- **Princeton Algorithms (Sedgewick)** — Coursera oficial

### Brasil
- **FGV** — https://ebape.fgv.br/ e https://direitorio.fgv.br/ (direito, gestão pública)
- **USP** — https://www5.usp.br/ (FMUSP saúde, IME CS)
- **UFMG** — https://ufmg.br/ (Medicina, Computação)
- **Fiocruz** — https://portal.fiocruz.br/ (saúde pública, epidemiologia; VideoSaúde)
- **IMPA** — https://impa.br/ (matemática)

### Saúde — cursos abertos
- **Harvard Medical School — HarvardX** — https://www.edx.org/school/harvardx
- **Johns Hopkins Coursera** (Epidemiologia, Saúde Pública)
- **USP — edX** — https://www.edx.org/school/uspx

## Critérios de inclusão

- Material aberto ou com acesso legítimo.
- Autor reconhecível na instituição.
- Preferir material com **data de atualização explícita**.

## Regras

- Curso → arquivo `<instituicao>-<codigo>.md` com frontmatter `titulo`, `instituicao`, `autor`, `ano`, `url`, `evidence_level: academico`, `bloco_relacionado`.
- Anotações pessoais sobre o curso não vão aqui — vão para `15_memory/promoted/<bloco>/`.
- Certificados emitidos → referenciar em `11_personal_skill_mapping/` como evidência.

## TODO

- Mapear cursos já feitos vs fila de interesse.
- Criar `_ranking.md` com ordem de prioridade por bloco.
