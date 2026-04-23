---
titulo: "Regras de Qualidade de Fonte"
bloco: "00_governance"
versao: "1.0"
status: "ativo"
ultima_atualizacao: 2026-04-23
---

# Regras de Qualidade de Fonte

## Classificação por tipo
1. **Oficial/normativa** — leis, resoluções CFM/CNJ/ANPD, normas ISO/NIST, RFC, especificações W3C/WHATWG/HL7/NEMA, documentação oficial de produto.
2. **Universitária** — manual clássico adotado em curso de graduação/pós de instituição reconhecida (Tanenbaum, CLRS, Kleppmann, Silberschatz, Kurose).
3. **Livro técnico revisado** — editora estabelecida, autor com tração (O'Reilly, Manning, Packt com crítica, Addison-Wesley, Pragmatic).
4. **Periódico revisado por pares** — journals com peer review, indexados (PubMed, IEEE, ACM, Scielo).
5. **Roadmap curado / curso estruturado** — roadmap.sh, cursos de universidade online (MIT OCW, Stanford, USP), cursos pagos reconhecidos (com crítica).
6. **Documentação técnica primária** — docs de projeto open source mantido (Postgres, Python, React, FastAPI).
7. **Artigo secundário** — posts técnicos de engenheiros reconhecidos, blogs de empresa de engenharia (Netflix, Stripe, Vercel, Anthropic).
8. **Comunidade** — StackOverflow, Reddit, Dev.to, Medium, HN.
9. **Não confiável** — conteúdo sem autoria verificável, SEO-spam, cursos-promessa, IA sem revisão humana.

## Critérios de aceite mínimo
Para entrar em `12_sources/`:
- Autoria identificável (pessoa ou organização).
- Data de publicação/última atualização conhecida.
- URL estável OU DOI/ISBN OU arquivamento (archive.org/Wayback).
- Idioma: pt-BR, en, es. Outros exigem justificativa.
- Licença compatível com citação (fair use técnico basta para referência).

## O que descartar de imediato
- Conteúdo plagiado ou sem atribuição.
- Artigo gerado por IA sem revisão humana declarada.
- Curso com promessa de salário/emprego/colocação.
- Blog sem autor identificado.
- Fonte com link morto e sem arquivamento.
- Material desatualizado em área de alta mudança (IA > 18 meses, web > 36 meses) sem nota de contexto histórico.

## Mapeamento tipo → nível de evidência padrão
Ver `evidence_levels.md`. Regra curta:
- Oficial/normativa → A
- Universitária clássica → B
- Livro técnico sólido / doc oficial de produto → B ou C
- Periódico revisado → A ou B (depende da força do estudo)
- Roadmap curado → C ou D
- Artigo secundário de engenheiro reconhecido → D
- Comunidade → E
- Não confiável → F (não entra; pode ficar em `inbox/` como pista)

## Revisão e aposentadoria
- Auditoria trimestral: link-check + checagem de atualização.
- Fonte substituída por versão oficial mais recente → mover para status `depreciado` com link para substituta.
- Fonte que perdeu autor/repositório → nível cai 1 grau; se B cai para D direto.

## Citações em artefatos
- Toda afirmação não trivial precisa citar pelo menos 1 fonte catalogada.
- Para nível A–B: citação única aceitável.
- Para nível C–D: idealmente 2 fontes independentes.
- Para nível E: no mínimo 2 fontes convergentes + marcar artefato como `nivel_evidencia: E`.

## Proibido
- Citar fonte sem lê-la.
- Fabricar DOI, ISBN, URL.
- Atribuir nível de evidência acima do tipo real para promover artefato.
