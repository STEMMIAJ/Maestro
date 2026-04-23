---
titulo: "Qualidade de dados — dimensões e checklist"
bloco: "06_data_analytics/data_engineering_basics"
tipo: "referencia"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 7
---

# Qualidade de dados

Dado de má qualidade fura qualquer análise. Em perícia, um CPF errado ou data trocada pode mudar conclusão. Medir qualidade é parte do pipeline — não opcional.

## 4 dimensões clássicas

### 1. Completude

Quanto do campo está preenchido vs. ausente.

- Métrica: `1 - (nulos / total)`.
- Exemplo: coluna `cpf` em `processos` está 87% preenchida → 13% inutilizáveis para join com CNES/PEP.
- Meta aceitável depende do campo — chave primária exige 100%.

### 2. Consistência

Dados não se contradizem entre campos, tabelas ou fontes.

- Inter-campo: `data_entrega >= data_nomeacao`.
- Inter-tabela: todo `laudo.processo_id` existe em `processos.id` (FK válida).
- Inter-fonte: mesma movimentação no DATAJUD e no DJEN — datas batem?
- Formato: CPF sempre 11 dígitos; CNJ sempre 20 dígitos.

### 3. Acurácia

Dado corresponde à realidade.

- Validação cruzada com fonte autoritativa (CNES para estabelecimentos, Receita para CPF/CNPJ).
- Regras de negócio: valor_causa > 0; idade ∈ [0, 120].
- Revisão manual amostral (ex.: 5% por lote).

### 4. Timeliness (atualidade)

Dado está disponível dentro da janela útil.

- Métrica: `data_atualização - data_evento`.
- Exemplo: publicação saiu no DJEN ontem, pipeline só viu hoje → latência 24 h. Aceitável para laudo mensal; inaceitável para audiência amanhã.
- SLA interno: DATAJUD 12 h, DJEN 2 h.

## Dimensões complementares

- **Unicidade**: sem duplicatas por chave (CNJ único em `processos`).
- **Validade**: formato/domínio corretos (tribunal ∈ lista oficial do CNJ).
- **Integridade referencial**: FK cumpridas.

## Checklist operacional

Antes de publicar dado no destino:

- [ ] Contagem de linhas comparada com run anterior (±30%)?
- [ ] Nulos por coluna dentro do esperado?
- [ ] Chaves primárias únicas?
- [ ] Faixas numéricas plausíveis (mín, máx, média)?
- [ ] Datas dentro da janela lógica?
- [ ] FKs resolvidas (zero órfãos)?
- [ ] Encoding UTF-8 consistente (sem "JOSÃ‰" em vez de "JOSÉ")?
- [ ] Campos obrigatórios 100% preenchidos?

## Implementação simples em SQL

```sql
-- Nulos por coluna
SELECT
  SUM(CASE WHEN numero_cnj IS NULL THEN 1 ELSE 0 END) AS nulls_cnj,
  SUM(CASE WHEN tribunal   IS NULL THEN 1 ELSE 0 END) AS nulls_trib,
  COUNT(*) AS total
FROM processos;

-- Duplicatas por chave
SELECT numero_cnj, COUNT(*) AS n
FROM processos GROUP BY numero_cnj HAVING n > 1;

-- FK órfã
SELECT l.id
FROM laudos l LEFT JOIN processos p ON p.id = l.processo_id
WHERE p.id IS NULL;

-- Range check
SELECT MIN(valor_causa), MAX(valor_causa), AVG(valor_causa) FROM processos;
```

## Ferramentas

- **Great Expectations** (Python): regras declarativas + relatório HTML.
- **dbt tests**: `not_null`, `unique`, `relationships`, `accepted_values` nativos.
- **Soda Core**: YAML de regras + CLI.
- **pandas-profiling / ydata-profiling**: relatório exploratório rápido.

Em projeto pequeno (perito solo), começar com **SQL de verificação** + log + alerta no Telegram. Não precisa framework.

## Política de falha

- **Falha bloqueante**: schema quebrou, PK duplicada, FK órfã → interromper pipeline, não sobrescrever destino.
- **Falha degradada**: completude caiu 5 p.p. → logar + alerta, seguir.
- **Falha silenciosa é proibida**: nunca `try/except` sem logar motivo.

## Rotina mensal

- Rodar perfil completo (pandas-profiling) e salvar HTML datado.
- Comparar com perfil anterior — mudança brusca = investigar.
- Registrar em `DIARIO-DO-SISTEMA.md` qualquer ajuste de regra de limpeza.
