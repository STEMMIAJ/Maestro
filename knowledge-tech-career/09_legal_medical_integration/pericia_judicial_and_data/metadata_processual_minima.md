---
titulo: Metadata processual mínima
bloco: 09_legal_medical_integration
tipo: referencia
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: pratica-consolidada
tempo_leitura_min: 4
---

# Metadata processual mínima

Campos canônicos que TODO processo cadastrado no sistema Dexter deve carregar. Sem eles, busca e roteamento quebram.

## Campos obrigatórios

### Numeração

- `cnj` — número único nacional, formato `NNNNNNN-DD.AAAA.J.TR.OOOO` (20 dígitos + separadores).
  - Ex.: `5001234-56.2026.8.13.0024`.
  - Validar dígito verificador (módulo 97, CNJ Res. 65/2008).
- `numero_antigo` — se migrado de numeração pré-CNJ.

### Jurisdição

- `tribunal` — sigla (TJMG, STJ, TRF1, TST).
- `tribunal_segmento` — `estadual | federal | trabalho | eleitoral | militar | superior`.
- `vara` — nome da vara (ex.: "2ª Vara da Fazenda Pública de Belo Horizonte").
- `vara_id_cnj` — código da vara na estrutura CNJ.
- `comarca` — nome + UF.
- `instancia` — `1 | 2 | superior`.
- `orgao_julgador_id` — PK no PJe/Datajud.

### Classe e assunto

- `classe_cnj` — código e nome (ex.: `436 - Procedimento Comum Cível`).
- `assunto_cnj` — código e nome (pode ser múltiplo, lista).
- `assunto_principal` — o primeiro ou o mais relevante.

Tabelas oficiais CNJ:
- Classes: `https://www.cnj.jus.br/sgt/consulta_publica_classes.php`
- Assuntos: `https://www.cnj.jus.br/sgt/consulta_publica_assuntos.php`

[TODO/RESEARCH: URL atual das tabelas em 2026]

### Partes

```json
{
  "partes": [
    {"polo": "ativo", "tipo": "autor", "nome": "...", "cpf_cnpj": "***.123.***-**", "advogados": [{"nome": "...", "oab": "OAB/MG 12345"}]},
    {"polo": "passivo", "tipo": "reu", "nome": "...", "cpf_cnpj": "...", "advogados": [...]},
    {"polo": "terceiro", "tipo": "assistente_litisconsorcial", "nome": "..."}
  ]
}
```

Polo: `ativo | passivo | terceiro`.
Tipo: `autor | reu | litisconsorte | assistente | intervenor | mpf | procurador`.

Mascarar CPF parcial em armazenamento (LGPD). Hash completo só em cofre.

### Atores do juízo

- `juiz` — nome + matrícula (pode mudar; guardar histórico).
- `promotor` — se houver intervenção do MP.
- `procurador_estado` / `procurador_municipio` — em ações contra poder público.
- `perito_nomeado` — nome + CRM + data de nomeação.

### Fase e status

- `fase_atual` — `conhecimento | recursos | cumprimento_sentenca | execucao | arquivado`.
- `status_processo` — `em_andamento | sobrestado | suspenso | arquivado | baixado`.
- `data_distribuicao` (ISO).
- `data_ultima_movimentacao` (ISO).
- `prazo_atual` — `{tipo: "laudo | manifestacao", data_limite: "2026-05-15"}` — quando aplicável.

### Valores

- `valor_da_causa` — decimal em R$.
- `honorarios_periciais_arbitrados` — decimal.
- `data_arbitramento` (ISO).
- `deposito_honorarios` — `{data, valor, alvara_expedido: bool}`.

### Documentos

- `documentos` — lista com `{id, tipo, paginas, data_juntada, juntante}`.
- `total_paginas` — para planejar carga.

### Identificadores externos

- `id_pje` — chave interna do PJe.
- `id_datajud` — `_id` no índice Elasticsearch.
- `link_pje` — URL direta se aplicável.

## Campos derivados (calculados)

- `urgencia_score` — função de prazo restante + complexidade.
- `especialidade_provavel` — inferida por `assunto_cnj` + palavras no resumo.
- `prioridade` — `alta | media | baixa` segundo regras do Dr. Jesus.

## Schema canônico (esqueleto)

```json
{
  "cnj": "string, validado",
  "tribunal": "string",
  "vara": "string",
  "comarca": "string",
  "classe": {"codigo": "int", "nome": "string"},
  "assuntos": [{"codigo": "int", "nome": "string", "principal": "bool"}],
  "partes": [...],
  "juiz": "string",
  "perito_nomeado": {...},
  "fase": "string",
  "status": "string",
  "datas": {"distribuicao": "date", "ultima_movimentacao": "date"},
  "valores": {"causa": "decimal", "honorarios": "decimal"},
  "documentos": [...],
  "id_pje": "string",
  "id_datajud": "string"
}
```

## Por que isso importa

- Busca unificada entre tribunais exige campos canônicos.
- Filtros de dashboard (ex.: "todos os processos da 5ª Vara de BH com prazo < 15 dias") só funcionam com metadata estruturada.
- Estatística pessoal (produtividade, distribuição por tribunal, tempo médio por laudo) depende de rotulagem consistente.
- Integração DataJud / PJe-MCP retorna dados nesse formato; só canonizar.

## Referências

- CNJ Resolução 65/2008 (numeração única).
- `~/Desktop/STEMMIA Dexter/DOCS/datajud/DATAJUD-GUIA.md`
- Tabelas CNJ de classe/assunto.
