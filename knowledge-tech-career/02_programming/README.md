---
titulo: Programacao
bloco: 02_programming
versao: 0.1
status: esqueleto
ultima_atualizacao: 2026-04-23
---

# 02 — Programação

## Definição do domínio

Programação é a tradução de um problema definido em instruções executáveis por máquina, com garantia de corretude e custo previsível de manutenção. Este bloco cobre lógica e algoritmos, as duas linguagens operacionais do sistema (Python e JavaScript), uso de terminal, controle de versão com Git, testes/debug e princípios de design de software.

Não é um curso de linguagem. É um mapa de competências: o que precisa estar dominado para ler código alheio, modificar um script com segurança e escrever automação que não quebra no dia seguinte.

Ênfase deliberada em Python (automação, dados, IA) e JavaScript (web, integrações), que cobrem 90% das necessidades práticas do dono do sistema.

## Subdomínios

- `logic_algorithms/` — variáveis, controle de fluxo, estruturas de dados, complexidade (O grande), recursão.
- `python/` — sintaxe, stdlib, pacotes (pip, venv), pandas, requests, tipagem.
- `javascript/` — ES moderno, async/await, Node.js, npm, fetch, DOM básico.
- `bash_terminal/` — shell POSIX, pipes, permissões, processos, zsh no macOS.
- `version_control_git/` — conceitos (commit, branch, merge, rebase), fluxo GitHub, resolução de conflito.
- `testing_debugging/` — testes unitários, pytest, debugging com breakpoint, logs estruturados.
- `software_design/` — SOLID, separação de responsabilidades, nomeação, refactor incremental.

## Perguntas que este bloco responde

1. Quando usar lista, dicionário, set ou tupla em Python?
2. O que é async/await e quando evita travar o programa?
3. Como versionar um projeto sem perder trabalho em merge?
4. Como escrever teste que falha antes de corrigir bug (TDD)?
5. Por que não usar `except:` sem tipo em Python?
6. Como debugar script que "às vezes" falha?
7. Qual a diferença entre `pip install` e `pip install -e .`?
8. Quando refatorar e quando reescrever?

## Como coletar conteúdo para este bloco

- Documentação oficial Python (docs.python.org) e MDN (JS).
- Livros: "Fluent Python" (Ramalho), "Eloquent JavaScript" (Haverbeke), "Pragmatic Programmer".
- Pro Git book (git-scm.com/book) como referência Git.
- Katas de algoritmo (Exercism, LeetCode) para exercício estruturado.
- Código real dos scripts do sistema pericial como caso de estudo.

## Critérios de qualidade das fontes

Seguir `00_governance/source_quality_rules.md`. Versão da linguagem sempre registrada (Python 3.12+, Node LTS). Preferir PEP/TC39 sobre blog. Código de exemplo deve rodar; se não roda, não entra.

## Exemplos de artefatos que podem entrar

- Cheatsheet Python (tipos, comprehensions, context managers).
- Template de projeto Python com pyproject.toml, ruff, pytest.
- Fluxo Git visual (commit → branch → PR → merge → tag).
- Checklist de code review de script de automação.
- Snippet library: scripts curtos comentados por problema resolvido.
- Guia de mensagens de commit convencionais.

## Interseções com outros blocos

- `01_ti_foundations` — processo, memória, SO sustentam entendimento de runtime.
- `03_web_development` — JS e Python backend puxam daqui.
- `04_systems_architecture` — design de software é porta de entrada para arquitetura.
- `06_data_analytics` — Python + pandas é base do trabalho com dados.
- `08_ai_and_automation` — scripts de automação e agentes usam esta base.
- `14_automation` — pipelines operacionais consomem padrões desta pasta.
