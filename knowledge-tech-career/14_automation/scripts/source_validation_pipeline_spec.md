---
titulo: Source Validation Pipeline — spec
tipo: spec_pipeline
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
---

# Source Validation Pipeline

**Objetivo**: verificar se links em `12_sources/**` ainda funcionam e se o autor/instituição é confiável conforme `evidence_levels` definidos em `00_governance/`.

## Entradas

- `12_sources/**/*.md` — fontes catalogadas.
- `00_governance/evidence_levels.md` (TODO confirmar path) — define níveis `oficial`, `academico`, `profissional`, `comunidade`, `inferencial`.
- Opcional: `12_sources/_authors.yaml` (TODO criar) — whitelist/blacklist de autores conhecidos.

## Saída

- `13_reports/master_summaries/source_validation_YYYY-MM-DD.md`:
  - tabela `url | status_http | last_checked | arquivo_origem | evidence_level | autor_status`
  - seção "links quebrados" (HTTP 4xx/5xx, DNS fail, TLS expirado)
  - seção "autor rebaixado" (evidence_level no arquivo > nível real do autor)
  - seção "fontes sem frontmatter `autor`/`evidence_level`"
- `13_reports/automation_logs/YYYY-MM-DD_source_validation.jsonl`.

## Algoritmo

1. **Extrair links** — regex markdown + `<a href>`. Resolver links relativos antes de tentar HTTP.
2. **HTTP HEAD** com fallback GET, timeout 10s, respeita `robots.txt`? (RESEARCH — decidir política).
   - User-agent identificado: `knowledge-tech-career/0.1 (+maestro)`.
   - Rate limit: máx 4 req/s globais, 1 req/s por host.
3. **Classificar status**:
   - `ok` (2xx), `redirected` (3xx — registrar destino novo), `gone` (404/410), `error` (5xx/timeout).
4. **Checar autor** — cruzar campo `autor` do frontmatter com `_authors.yaml`:
   - `oficial`: domínio em lista (planalto.gov.br, cnj.jus.br, cfm.org.br, anvisa.gov.br, python.org, mozilla.org...).
   - `academico`: domínio .edu, .ac.uk, usp.br, mit.edu; ou DOI presente.
   - `profissional`: blog de profissional reconhecido (manter lista explícita).
   - `comunidade`: StackOverflow, Reddit, Medium.
   - `inferencial`: IA, LLM output, opinião sem fonte.
5. **Divergência** — se frontmatter diz `oficial` mas domínio é Medium → flag.
6. **Arquivar Wayback** (opcional, `--archive`): submeter URL a web.archive.org/save/ para preservar.

## Regras

- Jamais editar `12_sources/`. Apenas relatar.
- Respeitar `noindex`/`nofollow` em arquivos `.ignore` dentro de `12_sources/` (TODO definir).
- Cache de resultados em `13_reports/_cache/source_validation.sqlite` com TTL 30d.

## Invocação

```
python ~/stemmia-forense/automacoes/source_validation.py \
  --repo "~/Desktop/STEMMIA Dexter/knowledge-tech-career" \
  --since 30d
```

## TODO / RESEARCH

- Decidir tratamento de paywalls (NEJM, JAMA) — HEAD retorna 200 mas conteúdo bloqueado. Heurística via `cite_as` DOI.
- Integração com Crossref para validar DOIs.
- Verificar TLS expiry (`ssl.getpeercert()`) — reporta, não bloqueia.
- Política para links de PDF hospedados em drives particulares (Dropbox, Drive) — marcar como `volatil`.
