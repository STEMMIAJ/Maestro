# COWORK — Escritório Digital (Perícia + Advocacia)

**Criado:** 2026-04-20
**Proprietário:** Dr. Jesus (perito judicial, CRM ativo)
**Objetivo:** Hub unificado que substitui o trabalho manual repetitivo por execução automática a partir de templates + dados estruturados.

---

## Filosofia (uma linha cada)

1. **Template + dados = documento.** Nunca redigir manualmente o que pode ser preenchido.
2. **Uma fonte de verdade.** Cada template existe em UM lugar (`02-BIBLIOTECA`), referenciado em todos os outros.
3. **Pasta-template replicável.** Caso novo = `cp -r _TEMPLATE-CASO/ <numero-processo>/`.
4. **Aprendizado contínuo.** Cada caso alimenta `06-APRENDIZADO/`.
5. **Zero trabalho manual.** Se está fazendo 2ª vez, virou automação.

---

## Mapa da pasta

| Pasta | Função | Estado |
|---|---|---|
| `00-INDICE/` | Mapa, plano de ação, decisões | ativo |
| `01-CASOS-ATIVOS/` | Processos em andamento (1 pasta/caso) | vazio (aguarda 1º caso) |
| `01-CASOS-ATIVOS/_TEMPLATE-CASO/` | Esqueleto replicável | criado |
| `02-BIBLIOTECA/` | Templates, modelos, cláusulas padrão | symlinks prontos |
| `03-IDENTIDADE/` | Timbrado, assinatura, dados profissionais | aguarda inputs |
| `04-PIPELINES/` | Receitas MD (análise, petição, laudo, revisão) | em construção |
| `05-AUTOMACOES/` | Skills, hooks, scripts, slash commands | em construção |
| `06-APRENDIZADO/` | Padrões detectados, erros, feedback loop | vazio |
| `07-ARQUIVO/` | Casos encerrados | vazio |
| `INBOX/` | Triagem de documentos novos | vazio |

---

## Como usar no dia a dia

```
Caso novo chega → joga PDFs em INBOX/
Pede ao Claude: "/novo-caso 0000000-00.0000.0.00.0000"
  → copia _TEMPLATE-CASO/ com o número
  → move PDFs do INBOX
  → roda análise rápida
  → gera FICHA.json

Precisa peticionar → "/peticao aceite" (ou proposta, esclarecimento, etc.)
  → lê FICHA.json
  → preenche template
  → aplica timbrado
  → salva em 01-CASOS-ATIVOS/<numero>/peticoes-geradas/
  → abre PDF final
```

---

## Links internos

- [PLANO-ACAO.md](PLANO-ACAO.md) — Fases, dependências, perguntas abertas
- [REPLICABILIDADE.md](REPLICABILIDADE.md) — Como aplicar esta estrutura em outros projetos
- [../02-BIBLIOTECA/_INDICE.md](../02-BIBLIOTECA/_INDICE.md) — Catálogo de templates
- [../03-IDENTIDADE/dados-profissionais.md](../03-IDENTIDADE/dados-profissionais.md) — Fonte de verdade dos dados
- [../04-PIPELINES/_INDICE.md](../04-PIPELINES/_INDICE.md) — Todas as receitas
- [../05-AUTOMACOES/_INDICE.md](../05-AUTOMACOES/_INDICE.md) — Skills e scripts
