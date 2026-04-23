---
titulo: Books — livros canônicos por bloco
tipo: readme_fonte
versao: 0.1
status: ativo
ultima_atualizacao: 2026-04-23
evidence_level_padrao: academico
---

# 12_sources/books

Livros canônicos por bloco do mapa de conhecimento. Confiança alta quando autor/editora são reconhecidos; ainda assim passar por `evidence_level` conforme `00_governance/`.

## Núcleo por bloco

### 02_programming
- **SICP** — Abelson & Sussman, *Structure and Interpretation of Computer Programs* (MIT).
- **Crafting Interpreters** — Robert Nystrom (gratuito online, https://craftinginterpreters.com).
- **The Pragmatic Programmer** — Hunt & Thomas (20th anniv).
- **Fluent Python** — Luciano Ramalho (2ª ed).
- **Python Cookbook** — Beazley & Jones.

### 03_web_development
- **HTTP: The Definitive Guide** — Gourley et al.
- **High Performance Browser Networking** — Ilya Grigorik (gratuito).
- **Designing Web APIs** — Jin, Sahni, Shevat.

### 04_systems_architecture
- **Designing Data-Intensive Applications** — Martin Kleppmann (DDIA).
- **Database Internals** — Alex Petrov.
- **Systems Performance** — Brendan Gregg.
- **Site Reliability Engineering** — Google (gratuito, sre.google/books/).

### 05_security_and_governance
- **The Tangled Web** — Michal Zalewski.
- **Serious Cryptography** — Jean-Philippe Aumasson.

### 06_data_analytics
- **Storytelling with Data** — Cole Nussbaumer Knaflic.
- **Practical Statistics for Data Scientists** — Bruce, Bruce, Gedeck.

### 07_health_data
- **Epidemiology** — Leon Gordis (Gordis Epidemiology, 6ª).
- **Biostatistics: The Bare Essentials** — Norman & Streiner.
- **Clinical Prediction Models** — Ewout Steyerberg.

### 08_ai_and_automation
- **Deep Learning** — Goodfellow, Bengio, Courville (gratuito).
- **Pattern Recognition and Machine Learning** — Bishop.
- **Speech and Language Processing** — Jurafsky & Martin (3ª ed rascunho gratuito).
- **Designing Machine Learning Systems** — Chip Huyen.

### 09_legal_medical_integration
- **Medicina Legal** — Genival Veloso de França.
- **Perícia Médica Previdenciária** — referências do INSS e CFM.
- **Tratado de Perícias Médico-Legais** — Hygino Hércules.
- TODO mapear referências próprias de Jesus já em uso.

### 10_career_map
- **So Good They Can't Ignore You** — Cal Newport.
- **Deep Work** — Cal Newport.
- **The Manager's Path** — Camille Fournier (quando aplicável).

## Regras

- Arquivo por livro: `<autor-snake>_<titulo-snake>.md`.
- Frontmatter: `titulo`, `autor`, `edicao`, `ano`, `isbn`, `bloco`, `evidence_level`, `status_leitura` (`fila`, `lendo`, `lido`, `referencia`).
- Notas de leitura não vão aqui — vão para `15_memory/promoted/<bloco>/`.

## TODO

- Inventariar livros físicos e ebooks já possuídos.
- Marcar leituras confirmadas com link para notas em `15_memory/`.
