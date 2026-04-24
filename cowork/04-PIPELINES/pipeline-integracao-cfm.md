---
nome: pipeline-integracao-cfm
entrada: nome completo do médico + (opcional) UF
saida: _dados/cfm-<papel>.json com {crm, uf, rqe, especialidade, situacao, data_inscricao}
duracao_estimada: 30s-2min (depende de captcha)
agentes_envolvidos: [cfm-buscador (novo)]
---

# Pipeline — Integração CFM (busca de CRM/RQE/especialidade)

## Objetivo

Puxar automaticamente do portal CFM os dados profissionais de um médico citado no processo (réu, autor, ou testemunha técnica). Usado principalmente na **proposta de honorários** para justificar complexidade quando o réu tem especialização formal.

## Fontes possíveis (ordem de prioridade)

1. **Portal CFM** — `https://portal.cfm.org.br/busca-medicos` (oficial, lento, captcha ocasional)
2. **CRM estadual** (ex: CRMMG `https://crmmg.org.br/busca-medico`) — às vezes mais rápido
3. **Cache local** — `cowork/06-APRENDIZADO/cache-cfm.jsonl` (medicos já buscados, TTL 180 dias)

## Pré-requisitos

- `mcp-brasil` MCP instalado (pode ter tool CFM nativa — verificar antes)
- Alternativa: Playwright MCP + script Python em `05-AUTOMACOES/scripts/cfm_buscador.py`
- Se captcha: fallback manual (abre no Chrome, usuário resolve, sistema captura retorno)

## Passos numerados

### 1. Normalizar nome
- Remove títulos ("Dr.", "Dra.", "Prof.")
- Remove preposições duplicadas
- Uppercase
- Escreve em `_dados/cfm-query.txt`

### 2. Consultar cache local
- Lê `cowork/06-APRENDIZADO/cache-cfm.jsonl`
- Se hit e TTL válido → pula para passo 6
- Se hit e TTL expirado → segue para passo 3 mas marca "refresh"
- Se miss → segue para passo 3

### 3. Tentar MCP Brasil
- Tool: `mcp__mcp-brasil__search_tools` com query "CFM"
- Se existir tool direta → executa e coleta JSON
- Se sucesso → pula para passo 5

### 4. Fallback: Playwright no portal CFM
- Navega `https://portal.cfm.org.br/busca-medicos`
- Preenche nome
- Se UF conhecida, filtra
- Aguarda tabela resultado
- Se múltiplos → lista e pausa para desambiguação
- Se captcha → abre Chrome não-headless, usuário resolve, sistema continua
- Extrai: CRM, UF, situação, data inscrição, especialidades (com RQE)

### 5. Normalizar estrutura
```json
{
  "nome": "string",
  "crm": "12345",
  "uf": "MG",
  "situacao": "ATIVO|SUSPENSO|CASSADO|FALECIDO",
  "data_inscricao": "YYYY-MM-DD",
  "especialidades": [
    {"nome": "Cirurgia Vascular", "rqe": "5678", "origem": "CFM"}
  ],
  "fonte": "portal.cfm.org.br",
  "consultado_em": "YYYY-MM-DDTHH:MM:SS"
}
```

### 6. Gravar saída
- Escreve em `_dados/cfm-<papel>.json` (papel = reu, autor, testemunha-tecnica, assistente-reu, etc.)
- Appenda entrada em `06-APRENDIZADO/cache-cfm.jsonl`

### 7. Registrar uso no aprendizado
- Se demorou > 60s ou falhou → log em `06-APRENDIZADO/cfm-problemas.jsonl` para ajuste.

## Pontos de verificação

| Após passo | Verificar | Como |
|---|---|---|
| 5 | JSON válido | `jq . _dados/cfm-reu.json` não dá erro |
| 5 | Situação conhecida | valor ∈ {ATIVO, SUSPENSO, CASSADO, FALECIDO, INATIVO} |
| 6 | Cache atualizado | `grep "$nome" cache-cfm.jsonl` retorna linha |

## Erros comuns + fix

1. **Nome muito comum** → retorna múltiplos → pipeline pausa, mostra top 5 com CRM+UF+situacao, usuário escolhe.
2. **Captcha CFM** → fallback manual: Playwright abre janela, usuário resolve o reCAPTCHA visualmente.
3. **Portal CFM fora do ar** → tenta CRM estadual. Se também falhar, grava `_dados/cfm-reu.json` com `{erro: "portal_indisponivel", tentar_novamente: true}` e pipeline segue (proposta é gerada sem bloco CFM, usuário revisa).
4. **Médico com RQE em especialidade rara** → sistema consulta tabela de correspondência AMB/CFM em `cowork/02-BIBLIOTECA/doutrina/tabela-especialidades-cfm.md` (a popular).
5. **Nome com variações (Maria / Ma. / M.)** → script usa fuzzy match + confirma com usuário se match < 0.9.

## Uso nos pipelines

| Pipeline | Quando invoca CFM | Papel buscado |
|---|---|---|
| `pipeline-proposta-honorarios` (classe=erro-medico) | Passo 2 | réu (obrigatório), autor (se médico) |
| `pipeline-analise-processo` | Passo opcional pós-extração | todos os médicos citados |
| `pipeline-geracao-laudo` | Antes de citar especialista-réu | réu |

## Produto intelectual

O JSON CFM é citado literalmente na proposta:

> "O Réu é médico inscrito no CRM/MG sob nº 12345, possui RQE 5678 em Cirurgia Vascular (título reconhecido pelo CFM), atualmente em situação ATIVO — o que impõe ao Perito a necessidade de expertise equivalente para analisar tecnicamente os atos médicos impugnados, justificando a majoração do honorário pericial ora proposto."

## Ideias futuras

- Buscar **histórico disciplinar** (PAD/sindicância) via LAI nos CRMs — sobe score de complexidade.
- Cruzar **Lattes** do médico (publicações, formação) para fortalecer ainda mais fundamentação em casos de erro médico grave.
- **Dashboard**: para cada médico pesquisado, histórico de casos onde apareceu (útil para detectar "réu contumaz").
