---
titulo: Rastreabilidade de laudo
bloco: 09_legal_medical_integration
tipo: referencia
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: normativo
tempo_leitura_min: 5
---

# Rastreabilidade de laudo

## Por que é obrigatório

- **CFM Res. 2.217/2018** (Código de Ética Médica) + **Res. 2.056/2013** (perícia): perito responde civil, penal e administrativamente pela veracidade. Rastreabilidade = defesa documental.
- **LGPD (Lei 13.709/2018)**: dados de saúde são sensíveis (art. 5º, II); exigem registro de tratamento (art. 37), finalidade, base legal, retenção.
- **Marco Civil da Internet + CPC 464–480**: elementos eletrônicos só têm força probatória se houver integridade demonstrável.
- **Jurisprudência**: laudos impugnados com alegação de "IA sem supervisão humana" derrubam força probatória se perito não consegue demonstrar fluxo.

Sem rastreabilidade, uma impugnação bem colocada vira inversão de ônus — o perito vira parte.

## Camadas de rastreabilidade

### 1. Hash do PDF final

Gerar SHA-256 do PDF assinado. Guardar em log separado. Qualquer modificação posterior muda hash → prova que PDF é o original.

```python
import hashlib
with open("laudo.pdf", "rb") as f:
    sha = hashlib.sha256(f.read()).hexdigest()
```

Registrar `{laudo_id, cnj, sha256, timestamp}` em registro imutável (append-only).

### 2. Timestamp confiável

`datetime.utcnow().isoformat() + "Z"` no momento da geração. Para força probatória maior: **timestamp qualificado** (RFC 3161) via autoridade (ICP-Brasil oferece TSA — Time Stamping Authority).

Alternativa moderna: âncora em blockchain (OpenTimestamps) — custo zero, prova de existência antes da data X.

### 3. Log de decisão do perito

Para cada afirmação conclusiva no laudo, registrar:

- Fonte (documento, peça, exame com `doc_id`).
- Trecho literal que sustenta.
- Se houve uso de LLM: qual modelo, versão, temperature, prompt ID versionado.
- Se houve revisão humana: quem, quando, decisão (aceitar / alterar / rejeitar).

Formato: JSON append-only (JSONL).

```json
{"ts":"2026-04-23T14:00:00Z","laudo_id":"LAU-2026-0042","conclusao_id":"C01","fonte":"doc_15 p.42","trecho_literal":"…","gerado_por":"claude-opus-4-7","prompt_ver":"resposta_quesito@v0.3","revisao_humana":{"perito":"dr_jesus","acao":"aceitar"}}
```

### 4. Prova de origem (provenance)

Para cada documento que alimentou o laudo:

- Origem (download do PJe, upload manual, scan presencial).
- Timestamp do download.
- Hash original.
- Quem tinha acesso antes do perito.

Cadeia de custódia em processo pericial importa — defesa pode questionar se exame foi adulterado.

### 5. Versionamento

Git em:

- Ficha.json (histórico de edições).
- Template de laudo (versão do template usado).
- Prompts (versionar com semver).
- Agente `.md` (versionar `~/.claude/agents/`).

Commit a cada alteração; tag ao gerar laudo oficial (`laudo-LAU-2026-0042`).

### 6. Logs de LLM

Guardar, por chamada:

- Timestamp.
- Modelo (`claude-opus-4-7`).
- Prompt completo (após substituição de variáveis).
- Resposta completa.
- Tokens (input/output).
- Custo.
- Temperature, seed.
- Hash do prompt + hash da resposta.

Armazenamento: JSONL rotativo em `~/Desktop/STEMMIA Dexter/logs/llm-calls/{data}.jsonl`.

Retenção: mínimo 5 anos (prazo prescricional civil; 10 anos para contratos).

## Políticas operacionais

- Nenhum laudo sai sem sua `ficha.json` commitada.
- Nenhum laudo sai sem entrada correspondente no log de decisão.
- PDF assinado tem hash registrado em planilha-mestra `laudos_entregues.csv`.
- Backup diário (launchd 03h) copia logs + fichas + PDFs para destino externo (Time Machine, cloud cifrada).

## Template de registro por laudo

```json
{
  "laudo_id": "LAU-2026-0042",
  "cnj": "5001234-56.2026.8.13.0024",
  "pdf_sha256": "...",
  "gerado_em": "2026-04-23T14:00:00Z",
  "tsa_url_opentimestamps": "...",
  "assinado_com": {"certificado": "ICP-Brasil A3", "titular": "...", "crm": "..."},
  "ferramentas": {
    "template": "laudo_base@v1.4",
    "agentes": ["redator-laudo@v0.7", "revisor-laudo@v0.3", "verificador-100@v0.5"],
    "modelo_llm": "claude-opus-4-7",
    "pipeline_git_sha": "abc123def"
  },
  "revisao_humana": {"perito": "...", "duracao_min": 40, "alteracoes_manuais": 12},
  "fontes_utilizadas": ["doc_15", "doc_22", "exame_EXA-2026-0017"]
}
```

## LGPD — mínimos operacionais

- Dado de paciente em trânsito cifrado (TLS).
- Dado em repouso cifrado (FileVault no Mac + disco externo).
- Acesso restrito (senha + 2FA para cofre de fichas).
- Política de retenção documentada.
- Registro de tratamento (RIPD — Relatório de Impacto) se processar volume alto.
- Direito de acesso / correção: mecanismo para atender titular em 15 dias (art. 19).

## Referências

- CFM Res. 2.217/2018, 2.056/2013.
- LGPD art. 5, 7, 11, 37, 50.
- CPC art. 464–480.
- RFC 3161 (TSA).
- OpenTimestamps.
