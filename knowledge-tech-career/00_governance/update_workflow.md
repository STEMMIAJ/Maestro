---
titulo: "Fluxo de Atualização da Base"
bloco: "00_governance"
versao: "1.0"
status: "ativo"
ultima_atualizacao: 2026-04-23
---

# Fluxo de Atualização

## Fases
```
inbox → triagem → rascunho → revisão cruzada → promoção → indexação Maestro → ativo → revisão trimestral
```

## 1. Inbox
Pasta `inbox/` na raiz. Tudo novo entra aqui primeiro:
- Pedidos do Dr. Jesus (nota solta, link, PDF, screenshot).
- Fontes sugeridas por times.
- Rascunhos iniciais.

Regra: nada é publicado direto no bloco sem passar pela triagem.

## 2. Triagem (Orchestrator)
Em até 48h úteis do ingresso:
- Classifica tipo (`concept|howto|checklist|...`).
- Atribui bloco e time responsável.
- Decide descarte, retenção em inbox ou promoção a rascunho.
- Aplica naming conventions e cria arquivo `rascunho`.

Artefato sem autoria/objetivo claro volta para inbox com nota.

## 3. Rascunho (time responsável)
Time autor produz artefato seguindo:
- `taxonomy.md` para localização.
- `naming_conventions.md` para nome/frontmatter.
- `source_quality_rules.md` e `evidence_levels.md` para fontes.

Status frontmatter: `rascunho`. Pode viver até 30 dias. Além disso, Orchestrator pergunta causa.

## 4. Revisão cruzada
Todo artefato precisa de revisão de **pelo menos um time distinto do autor**. Revisor checa:
- Frontmatter válido e completo.
- Fontes existem em `12_sources/` e estão classificadas.
- Nível de evidência coerente com fontes.
- Afirmações testáveis testadas.
- Sem dado identificável.
- Referência cruzada a consumidores.

Aprovação → promoção. Reprovação → volta a rascunho com nota.

## 5. Promoção
Orchestrator muda status para `ativo`, adiciona a `INDEX.md`, registra em `TASKS_DONE.md`.

## 6. Indexação Maestro
Maestro Integration Team:
- Registra artefato no índice da base (embeddings/full-text se aplicável).
- Se for `template` ou `spec`, gera job correspondente em `14_automation/openclaw_jobs/` quando pertinente.
- Atualiza `summary_jobs_ativos.md` se criou job.

## 7. Revisão trimestral
Todo artefato `ativo` tem campo `proxima_revisao`. Default = publicação + 90 dias. Revisão confere:
- Link-check.
- Fontes ainda válidas (não depreciadas).
- Conteúdo ainda correto (especial atenção: IA > 6 meses, web > 12 meses, normas recém-alteradas).
- Uso real (citado por outros artefatos, ou morto?).

Resultado: renovação, atualização (bump de versão), depreciação, ou arquivamento em `99_attic/`.

## Gatilhos de revisão fora do ciclo
- Alteração normativa (nova resolução CFM/CNJ/ANPD).
- Vulnerabilidade de segurança CVE em dependência citada.
- Fonte principal depreciada/removida.
- Contradição interna detectada entre dois artefatos.
- Pedido explícito do Dr. Jesus.
- Incidente real (ex.: hook anti-limpeza nasceu de incidente).

## Artefatos periódicos (automáticos via Maestro)
- Mensal: `summary_bloco<NN>.md` por bloco, `summary_skills_YYYY_MM.md`, `summary_jobs_ativos.md`, `summary_fontes_por_bloco.md`.
- Trimestral: `report_mercado_br_ti_ia_YYYY_QN.md`, `report_link_check_YYYY_QN.md`, `report_riscos_dexter.md`, `report_gap_critico_YYYY_QN.md`, `report_execucoes_YYYY_MM.md` consolidado.

## Controle de mudança
Todo artefato `ativo` que muda bump de versão:
- `minor`: complemento, correção pequena.
- `major`: mudança conceitual ou de conclusão.

Registrar em seção `## Changelog` ao fim do próprio arquivo OU em `CHANGELOG.md` raiz. Nunca reescrever sem rastro.

## Proibições
- Publicar direto, pulando triagem ou revisão cruzada.
- Deletar artefato (arquivar em `99_attic/` com nota).
- Alterar nível de evidência sem registrar motivo.
- Artefato sem `proxima_revisao`.
