---
titulo: Roadmaps — trilhas curadas de aprendizado
tipo: readme_fonte
versao: 0.1
status: ativo
ultima_atualizacao: 2026-04-23
evidence_level_padrao: profissional
---

# 12_sources/roadmaps

Trilhas curadas por comunidades/empresas. Servem para **orientar ordem de estudo**, não como verdade técnica. `evidence_level: profissional` (comunidade especializada).

## Curados

- **roadmap.sh** — Kamran Ahmed. https://roadmap.sh/ — backend, frontend, devops, AI engineer, data engineer.
- **Frontend Masters — Learning Paths** — https://frontendmasters.com/learn/
- **Google — Research / ML Paths** — https://ai.google/education/ e https://research.google/careers/interns/
- **Full Stack Open** — Univ. Helsinki. https://fullstackopen.com/ (gratuito, rigoroso).
- **The Odin Project** — https://www.theodinproject.com/
- **OSSU — Open Source Society University (CS)** — https://github.com/ossu/computer-science
- **OSSU Data Science** — https://github.com/ossu/data-science

## IA / ML

- **Fast.ai** — Jeremy Howard. https://www.fast.ai/
- **DeepLearning.AI** — Andrew Ng. https://www.deeplearning.ai/
- **Chip Huyen — ML Interviews Book + Roadmap** — https://huyenchip.com/
- **Lil'Log (Lilian Weng)** — https://lilianweng.github.io/ (para estado da arte, não exatamente roadmap).

## Segurança

- **OWASP** — https://owasp.org/ (Top 10, ASVS, Cheat Sheets).
- **PortSwigger Web Security Academy** — https://portswigger.net/web-security (gratuito).

## Saúde / Perícia (TODO)

- Não há "roadmap.sh" equivalente para perícia médica BR. RESEARCH: construir roadmap próprio em `10_career_map/perito_judicial.md` referenciando CFM, resoluções, cursos.

## Regras

- Roadmap é **mapa de território**, não território. Ler, filtrar pelo próprio contexto, adaptar.
- Arquivo por roadmap: `<fonte>-<topico>.md` com frontmatter `titulo`, `autor`, `url`, `evidence_level: profissional`, `bloco_relacionado`.
- Cruzar cada roadmap escolhido com `10_career_map/` e `11_personal_skill_mapping/` — marcar itens já dominados.

## Não-objetivos

- Não tratar roadmap como autoridade final. Livros (`books/`) e docs oficiais (`official_docs/`) têm precedência em caso de conflito.
- Não copiar roadmap inteiro — linkar e anotar adaptação pessoal.

## TODO

- Selecionar 2–3 roadmaps-âncora por trilha ativa (AI Engineer, Backend, Saúde-Dados).
- Gerar diff "o que roadmap sugere vs o que já tenho" via pipeline skill_mapping.
