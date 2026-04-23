---
titulo: "Níveis de Evidência"
bloco: "00_governance"
versao: "1.0"
status: "ativo"
ultima_atualizacao: 2026-04-23
---

# Níveis de Evidência

Esquema hierárquico adaptado da medicina baseada em evidência para contexto técnico. Todo artefato declara no frontmatter `nivel_evidencia: A|B|C|D|E|F`.

## A — Oficial / Normativa
- Leis, decretos, resoluções (CFM, CNJ, ANPD, Anvisa).
- Normas ISO, NIST SP 800, ABNT.
- RFCs IETF, especificações W3C/WHATWG/HL7/NEMA.
- Constituição de linguagem/protocolo via docs oficiais do mantenedor.

Uso: afirmação sobre o que a norma manda. Evidência suficiente por si só.

## B — Universidade / Manual clássico / Periódico revisado forte
- Livros-texto canônicos de graduação/pós (Tanenbaum, CLRS, Kleppmann, Silberschatz, Kurose, Stevens).
- Meta-análise ou revisão sistemática em periódico indexado.
- White paper de organização de referência (Google, Anthropic research, OpenAI system card) quando descreve implementação própria.

Uso: fundamento conceitual e princípios. Isoladamente sustenta artefato.

## C — Documentação técnica primária / Livro sólido / Estudo primário
- Docs oficiais de produto OSS maduro (PostgreSQL, Python, FastAPI, React).
- Livros O'Reilly/Manning/Pragmatic de autor reconhecido.
- Paper de conferência top-tier (NeurIPS, ICML, OSDI, SIGMOD, CCS) — estudo primário.

Uso: base para howto e template. Prática verificada.

## D — Artigo secundário
- Posts de engenharia de empresa sólida (Netflix Tech Blog, Stripe, Stack Overflow, Vercel, Anthropic blog).
- Roadmap curado (roadmap.sh) com autoria visível.
- Curso estruturado de plataforma reconhecida (Coursera/edX universitário).

Uso: complemento. Exige 2 fontes convergentes para sustentar afirmação central.

## E — Comunidade / Blog individual
- StackOverflow, Reddit, Dev.to, Medium, HN, Twitter/X técnico.
- Blog pessoal sem revisão.
- Issue/PR em repositório (quando não é declaração oficial do mantenedor).

Uso: pista, contexto, exemplo. Nunca sustenta afirmação normativa sozinha.

## F — Não confiável
- Autor desconhecido, sem data.
- SEO-spam, conteúdo clonado.
- IA sem revisão humana.
- Curso-promessa.

Uso: **não entra na base**. Pode ficar em `inbox/` marcado para triagem/descarte.

## Como marcar no frontmatter
```yaml
nivel_evidencia: "B"
fontes:
  - source_kleppmann_ddia.md   # B
  - source_postgres_docs_v16.md # C
```

Se artefato cita fontes de níveis diferentes, o `nivel_evidencia` declarado é **o nível da afirmação central sustentada**, não a média nem o máximo. Regra: use o nível da fonte mínima necessária para sustentar a tese principal.

## Regras de promoção/rebaixamento
- Subir nível: só com fonte adicional de nível superior; requer revisão cruzada.
- Descer nível: qualquer auditor pode rebaixar citando motivo. Fica em `ultima_atualizacao` + nota no changelog do artefato.
- Artefato que dependia de fonte agora depreciada herda o rebaixamento até substituição.

## Uso prático por tipo de artefato
- `concept` → idealmente A–B.
- `howto` → C–D aceitável, desde que procedimento testado localmente.
- `checklist` → pode agregar D–E se itens são heurísticos — declarar no preâmbulo.
- `summary` / `report` → herda nível da fonte mais fraca que sustenta conclusão; **declarar abertamente**.
- `source` → registra nível da própria fonte.
- `template` → nível do conceito que ele instancia.
- `job` → C mínimo (especificação executável precisa de base sólida).

## Proibido
- Declarar nível A sem link direto à norma oficial.
- Inflar nível para promover artefato.
- Omitir rebaixamento quando fonte cai.
