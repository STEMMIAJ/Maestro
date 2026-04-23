---
titulo: Dados de perícia judicial — representação estruturada
bloco: 09_legal_medical_integration
tipo: referencia
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: pratica-consolidada
tempo_leitura_min: 6
---

# Dados de perícia judicial — representação estruturada

## Por que estruturar

Processo pericial lida com quesito + laudo + histórico + exames — dados heterogêneos, de fontes distintas, com relações complexas. Texto livre não permite busca, agregação, reuso. Representar em JSON canônico permite: pipelines, verificadores, templates, RAG estruturado, auditoria.

## Núcleo de 4 entidades

### 1. Quesitos

```json
{
  "id": "Q01",
  "autor": "juizo | autor | reu | assistente_tecnico_autor | assistente_tecnico_reu",
  "numero_original": "1",
  "texto_literal": "O autor apresenta nexo causal entre o acidente e a lombalgia atual?",
  "tipo": "causal | anatomico | funcional | temporal | quantificacao_dano | diagnostico | terapeutico",
  "peca_fonte": "inicial | contestacao | replica | despacho_saneador | impugnacao_laudo",
  "pagina_fonte": 42,
  "viabilidade_medica": "responde | ambiguo | fora_escopo | exige_perito_outra_area",
  "resposta": null,
  "status": "pendente | rascunho | finalizada"
}
```

### 2. Laudo (estrutura canônica)

```json
{
  "laudo_id": "LAU-2026-0042",
  "processo_cnj": "5001234-56.2026.8.13.0024",
  "perito": {"nome": "...", "crm": "CRM-MG 12345"},
  "data_entrega": "2026-05-10",
  "identificacao_pericia": {
    "tipo": "medica | psiquiatrica | odontologica | estetica",
    "local_exame": "consultorio | domicilio | hospital",
    "data_exame": "2026-04-18"
  },
  "anamnese": {
    "queixa_principal": "...",
    "historia_doenca_atual": "...",
    "antecedentes": {"pessoais": "...", "familiares": "...", "ocupacionais": "..."},
    "medicamentos_em_uso": [{"nome": "...", "dose": "...", "via": "..."}]
  },
  "exame_fisico": {
    "geral": "...",
    "segmentar": {"cabeca": "...", "pescoco": "...", "torax": "...", "abdome": "...", "mmss": "...", "mmii": "..."},
    "testes_especificos": [{"nome": "Lasegue", "resultado": "positivo 45 graus"}]
  },
  "exames_complementares": [
    {"tipo": "RM lombar", "data": "2026-03-12", "resultado": "...", "fonte_peca": "doc_15"}
  ],
  "discussao": "...",
  "conclusao": "...",
  "respostas_quesitos": [{"quesito_id": "Q01", "resposta": "..."}],
  "cid_principal": "M54.5",
  "cids_secundarios": ["M51.1"],
  "incapacidade": {"existe": true, "tipo": "parcial_temporaria", "duracao_dias": 90}
}
```

### 3. Histórico clínico

```json
{
  "paciente_id": "hash_anonimizado",
  "eventos": [
    {
      "data": "2024-03-15",
      "tipo": "consulta | exame | cirurgia | internacao | medicacao | atestado",
      "profissional": {"nome": "...", "crm": "...", "especialidade": "..."},
      "local": "...",
      "resumo": "...",
      "documentos": ["doc_8"],
      "cid_associado": "M54.5"
    }
  ]
}
```

Ordenado cronologicamente. Permite detectar lacunas, contradições, saltos.

### 4. Exames

```json
{
  "exame_id": "EXA-2026-0017",
  "tipo": "RM | TC | RX | laboratorial | EMG | audiometria | ...",
  "data_coleta": "2026-03-12",
  "data_laudo": "2026-03-13",
  "laboratorio_ou_clinica": "...",
  "medico_responsavel": "...",
  "achados_estruturados": [
    {"regiao": "L4-L5", "achado": "protrusao discal central", "gravidade": "moderada"},
    {"regiao": "L5-S1", "achado": "normal", "gravidade": null}
  ],
  "impressao_diagnostica": "...",
  "arquivo_original": "doc_42.pdf",
  "pagina_no_processo": 128,
  "hash_sha256": "..."
}
```

## Campos mínimos (MUST HAVE)

Qualquer pipeline pericial do Dexter deve guardar, no mínimo:

- `processo_cnj`, `vara`, `comarca` (ver `metadata_processual_minima.md`).
- Lista de documentos com: `id`, `tipo`, `pagina_inicial`, `pagina_final`, `hash`, `data`.
- Lista de quesitos com `id`, `texto_literal`, `autor`.
- Cronologia de eventos clínicos.
- CIDs e sua fonte (prontuário, laudo, declarado).
- Assinaturas digitais / timestamps de cada peça.

## Convenções

- **Datas**: ISO 8601 (`YYYY-MM-DD`) sempre.
- **Texto_literal**: preservar grafia original, mesmo com erros. Errata separada em campo.
- **IDs**: prefixo por tipo (Q, LAU, EXA, DOC) + número sequencial.
- **Fontes**: toda asserção derivada tem `fonte_id` apontando para documento-prova.
- **Null vs vazio**: `null` = não consta; `""` = consta vazio; ausência = não aplicável.

## Armazenamento

- Estrutura canônica JSON: `~/Desktop/STEMMIA Dexter/dados/processos/{cnj}/ficha.json`.
- Documentos brutos: `.../docs/{doc_id}.pdf` + `.../docs/{doc_id}.txt` (OCR).
- Versionamento: git em pasta de fichas; commit a cada alteração.
- Índice: SQLite central com PK `cnj` para consulta rápida.

## Por que vale o esforço

- Template de laudo consome ficha.json e preenche placeholders (ver `document_automation/geracao_de_laudo_com_template.md`).
- RAG fica pequeno e preciso (só o que é campo relevante).
- Auditoria: qualquer afirmação no laudo rastreia até fonte (ver `auditability_traceability/rastreabilidade_de_laudo.md`).
- Aprendizado entre processos: dados estruturados permitem estatística pessoal ("em quantos casos CID M54.5 resultou em incapacidade permanente no meu histórico?").

## [TODO/RESEARCH]

- Padronizar schema em JSON Schema versionado.
- Cruzar com TUSS/SIA-SUS para tipagem de procedimento.
- Integrar CID-11 (BR migrando gradualmente).
