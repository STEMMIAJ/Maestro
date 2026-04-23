---
titulo: Fontes de Conhecimento
bloco: 12_sources
versao: 0.1
status: esqueleto
ultima_atualizacao: 2026-04-23
---

# 12 — Sources

## Definição do domínio
Catálogo hierarquizado das fontes usadas pela base. Toda afirmação técnica ou jurídica em qualquer bloco referencia uma fonte aqui. Hierarquia: docs oficiais > universidades > livros revisados > periódicos > roadmaps curados > cursos > comunidades.

## Subdomínios
- `official_docs/` — docs oficiais de linguagens, frameworks, padrões (Python.org, MDN, RFC, CNJ, CFM, ANPD)
- `universities/` — material aberto (MIT OCW, Stanford CS, Harvard CS50, USP, UFMG)
- `books/` — livros técnicos de referência, com ISBN
- `journals/` — periódicos revisados por pares (JAMA, Nature Digital Medicine, IEEE, ACM)
- `roadmaps/` — roadmap.sh, OSSU, Teach Yourself CS
- `courses/` — cursos pagos/gratuitos com avaliação
- `communities/` — fóruns, listas, Discords (StackOverflow, HN, Lobsters, subreddits técnicos)

## Perguntas que este bloco responde
- Onde está a fonte primária disso?
- Que livro ler antes de abrir o Stack Overflow?
- Que curso vale o tempo vs marketing?
- Que comunidade dá resposta técnica de qualidade?

## Como coletar conteúdo
- Indexar cada fonte já citada em blocos 01–10
- Adicionar metadados: autor, data, URL, arquivo local (se houver), confiabilidade (A/B/C)
- Deduplicar (mesma fonte citada em vários blocos → ficha única aqui)
- Revisar links semestralmente (link-rot é real)

## Critérios de qualidade
- Toda entrada tem: título, autor(es), ano, URL ou ISBN, nível de confiabilidade, data do último check
- Fontes nível A (docs oficiais, periódicos revisados) marcadas explicitamente
- Fontes nível C (blogs, vídeos YouTube) aceitas mas marcadas e só usadas quando A/B indisponível
- Link morto = atualizar ou marcar `[LINK_ROT]`

## Exemplos de artefatos
- Ficha-padrão de fonte (YAML frontmatter + resumo + por-que-confiar)
- Lista "top 20 fontes nível A por domínio"
- Script de verificação automática de link (planejado em `14_automation/`)
- Mapa fonte → blocos que a citam

## Interseções
- Todos os blocos (todos citam fontes daqui)
- `00_governance` (regra de citação obrigatória)
- `14_automation` (verificador de link)
