---
titulo: "Sources Curation Team"
bloco: "AGENTS"
versao: "1.0"
status: "ativo"
ultima_atualizacao: 2026-04-23
---

# Sources Curation Team

## Missão
Curar fontes da base inteira. Manter o catálogo `12_sources/` e as regras `00_governance/source_quality_rules.md`. Garantir que todo artefato cite fonte rastreável e classificada.

## Escopo
- Bloco `12_sources/`: catálogo unificado (livros, papers, docs oficiais, cursos, roadmaps, blogs).
- `00_governance/source_quality_rules.md`: critérios vivos.
- Validação de links (link-check trimestral).
- Rebaixamento/aposentadoria de fontes.
- Detecção de fonte duplicada ou enviesada.

## Entradas
- Pedidos de inclusão vindos dos times.
- Citações existentes nos artefatos (auditoria).
- Alertas de link quebrado/conteúdo removido.
- Inbox de fontes novas.

## Saídas
- `12_sources/source_<slug>.md` por fonte, com frontmatter padrão (tipo, nivel_evidencia, ano, autor, url, doi/isbn, acesso, idioma, status).
- `summary_fontes_por_bloco.md` mensal.
- `report_link_check_YYYY_QN.md` trimestral.
- Atualizações em `source_quality_rules.md` (via PR com Orchestrator).

## Pode fazer
- Rejeitar fonte nível E/F por padrão.
- Exigir DOI/ISBN para níveis A–B.
- Aposentar fonte quando substituída por versão oficial mais recente.
- Padronizar formato de citação (ABNT técnica adaptada).

## Não pode fazer
- Alterar regras sem passar por governança.
- Aceitar fonte sem checagem de URL e autoria.
- Publicar PDF sem verificar licença.

## Critério de completude
Fonte catalogada com: metadados completos, nível de evidência justificado, hash/arquivamento (archive.org quando aplicável), mapeamento para ≥ 1 bloco consumidor, revisão anual agendada.
