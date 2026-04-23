---
titulo: "Portfólio e Projeto Eficaz"
bloco: "10_career_map"
tipo: "pratica"
nivel: "junior-pleno"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 8
---

# Portfólio e Projeto Eficaz

Portfólio é evidência concreta de capacidade. Substitui "anos de experiência" para quem vem de outra área. Projeto medíocre no GitHub engana até o candidato, não o recrutador técnico.

## O que um projeto de portfólio precisa ter

### 1. README forte

Primeira coisa que o leitor vê. Em 60 segundos, entregar:

- **Título + 1 linha** do que faz.
- **Por quê existe** (problema resolvido).
- **Demo** — GIF curto, print, ou link para deploy.
- **Quick start** — como rodar em 3 comandos.
- **Stack** — linguagens, libs principais.
- **Status** — funcional, em construção, arquivado.
- **Testes** — como rodar + badge de cobertura.
- **Licença**.

Template mínimo:

```markdown
# Nome-do-Projeto

Breve descrição em 1-2 linhas.

![demo](docs/demo.gif)

## Por que

Problema concreto + público-alvo.

## Rodando

```bash
git clone ...
cd ...
make setup
make run
```

## Stack

- Linguagem X
- Framework Y
- BD Z

## Testes

`make test`

## Licença

MIT
```

### 2. Demo real

- GIF animado (LICEcap, Kap) mostrando interação.
- Deploy público gratuito (Vercel, Railway, Fly.io) quando fizer sentido.
- Screenshot em alta para projetos visuais.

Sem demo, leitor abandona. Exceção: biblioteca (exemplo de código no README substitui).

### 3. Commits limpos

- Mensagens no padrão Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`).
- Commits atômicos (um concern por commit).
- Histórico linear ou rebase antes do push.
- Sem "wip", "ajustes", "oops".

### 4. Testes

- Cobertura mínima 50% em lógica de negócio.
- CI rodando (GitHub Actions com badge verde).
- Teste que ensina o leitor como o módulo funciona.

### 5. Documentação de decisão (ADR)

Pasta `docs/adr/` com decisões arquiteturais:

```markdown
# ADR 001: Usar SQLite em vez de Postgres

Data: 2026-04-23
Status: Aceito

## Contexto
...
## Decisão
...
## Consequências
...
```

Mostra que o autor pensa, não só codifica.

### 6. CHANGELOG

`CHANGELOG.md` com versionamento. Mostra disciplina de release.

### 7. Issue tracker ativo

Uso das Issues do GitHub: bug report, roadmap, discussão. Mostra que o projeto vive.

## Escolha de projeto

Um projeto forte > cinco fracos.

### Critérios

- Resolve problema real do próprio autor ou de uma comunidade.
- Escopo executável em 4-12 semanas parcial.
- Dá oportunidade de exercitar stack-alvo.
- Produz resultado demonstrável em 60s.

### Exemplos eficazes para Dr. Jesus

1. **Dexter** — hub pericial (já existe). Precisa: README mestre forte, ADRs, testes.
2. **Monitor de Processos** — DJEN + DataJud + alertas (já existe). Precisa: CI, CHANGELOG, demo gif.
3. **Template de Laudo Reaproveitável** — CLI + biblioteca de placeholders (já existe). Documentar como open source parcial (sem vazar dado real).
4. **Analisador de Jurisprudência** — busca + sumarização com LLM local. Novo.

### Anti-exemplos

- To-do list clonado.
- Clone do Instagram.
- Boilerplate sem customização.
- Projeto morto há 2 anos.

## Template de estrutura de repositório

```
projeto/
├── README.md
├── LICENSE
├── CHANGELOG.md
├── .github/
│   └── workflows/ci.yml
├── docs/
│   ├── adr/
│   ├── demo.gif
│   └── arquitetura.md
├── src/
├── tests/
├── pyproject.toml (ou equivalente)
└── Makefile
```

## GitHub profile

Além dos repos individuais, o perfil em si é portfólio.

- Foto real e profissional.
- Bio: 1 linha do que faz + link para site/LinkedIn.
- Repos em destaque (pinned): 4-6 melhores.
- `README.md` no repo `username/username` com introdução e stack.
- Contribuição verde (não é critério absoluto, mas mostra atividade).

## Site pessoal / blog

Opcional, mas multiplicador de retorno.

- Portfólio em HTML estático (Astro, Hugo, Next).
- Blog com 4-8 posts técnicos bem escritos > 40 posts rasos.
- Artigos linkados no GitHub.

## Revisão externa

Antes de divulgar vaga/cliente:

- Pedir para 2 colegas técnicos revisarem o README em 3 min. Se não entenderem o projeto nesse tempo, reescrever.
- Rodar `git clone` em máquina limpa e seguir o próprio README. Falhou? Corrigir.

## Referência cruzada

- `../learning_paths/trilha_medico_para_tech.md`
- `../junior_pleno_senior/sinais_concretos_de_cada_nivel.md`
- `../role_expectations/expectativas_por_papel.md`
