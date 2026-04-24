# Pipeline ACEITE-A-PARTIR-NOMEACAO

**Pedido original (19/abr/2026):**
> "UM PIPELINE DE ANALISE DO PROCESSO A PARTIR DA MINHA NOMEACAO - VOCE VAI IDENTIFICAR A PAGINA QUE FUI NOMEADO, E DALI PRA FRENTE LER TODAS, E NAO SEI COMO VOCE VAI ENTENDER O QUE E PRA FAZER"

---

## Princípio
**Não ler o processo inteiro.** Ler do ponto da nomeação pra frente. Extrair só o que precisa para gerar petição de aceite. Pedir confirmação para situações novas. Aprender com o tempo.

---

## Organograma (ASCII)

```
┌──────────────────────────────────────────────────────────────────┐
│  ENTRADA: PDF do processo PJe (já baixado em ~/Desktop/...)     │
└─────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │ FASE 1 — DETECTAR NOMEAÇÃO    │
              │ (passo determinístico)        │
              └───────────────┬───────────────┘
                              │
   procura no texto, em ordem, qualquer um destes padrões:
   - "nomeio perito" / "nomeio o perito"
   - "perito judicial" + nome dele (Jésus Penna Noleto / CRM-MG 92148)
   - "designo perito" / "designo como perito"
   - "fica nomeado" / "fica designado"
   - decisão saneadora citando perícia médica
                              │
                              ▼
              ┌───────────────────────────────┐
              │ FASE 2 — RECORTAR              │
              │ Pega da página da nomeação    │
              │ até o final do PDF            │
              └───────────────┬───────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │ FASE 3 — EXTRAIR 6 CAMPOS     │
              └───────────────┬───────────────┘
                              │
       ┌──────────────────────┼──────────────────────┐
       │                      │                      │
       ▼                      ▼                      ▼
   HONORÁRIOS            LOCAL/ENDEREÇO       DATA LIMITE
   "R$ X,XX"             "Fórum Y" / endereço  "X dias" / data
   "fixo em"             paciente              "prazo de"
   "arbitro"
       │                      │                      │
       ▼                      ▼                      ▼
   QUESITOS              TIPO DE                JUIZ + VARA
   numerados             PERÍCIA               (gênero do juiz!)
   na decisão            (incapacidade,        para vocativo
                          DPVAT, AJ, etc)       correto
                              │
                              ▼
              ┌───────────────────────────────┐
              │ FASE 4 — DECIDIR SUBTIPO      │
              │ aceite simples                │
              │ aceite condicionado           │
              │ proposta de honorários        │
              │ escusa                        │
              │ mutirão                       │
              │ reagendamento                 │
              └───────────────┬───────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │ FASE 5 — VARIÁVEL DESCONHECIDA?│
              │ Se SIM → PARAR e perguntar    │
              │ Se NÃO → seguir               │
              └───────────────┬───────────────┘
                              │ exemplo: "ainda esperando mutirão"
                              │  Claude: "marco como pendente?"
                              │  Jésus: SIM/NÃO
                              │  → SIM → adiciona ao banco
                              │  → NÃO → ele instrui
                              │
                              ▼
              ┌───────────────────────────────┐
              │ FASE 6 — GERAR PETIÇÃO        │
              │ usa template do subtipo       │
              │ preenche campos extraídos     │
              └───────────────┬───────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │ FASE 7 — RASTREABILIDADE      │
              │ cada parágrafo da petição     │
              │ → mostra de onde tirou        │
              │ → checklist pra Jésus marcar  │
              └───────────────┬───────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │ FASE 8 — APRENDIZADO          │
              │ situação inédita → Claude     │
              │ pede confirmação              │
              │ Jésus aprova → vira regra     │
              │ no banco SQLite               │
              └───────────────┬───────────────┘
                              │
                              ▼
                   PETIÇÃO PRONTA + CHECKLIST
                   (Jésus revisa e protocola)
```

---

## Componentes que JÁ EXISTEM no seu sistema

Você não vai construir do zero. Já tem:

| Componente | Onde | O que faz |
|------------|------|-----------|
| `Triador de Petição` (agente) | `~/.claude/agents/` | classifica tipo de petição a partir de print PJe |
| `Padronizador de Estilo` (agente) | `~/.claude/agents/` | consulta perfil de estilo antes de redigir |
| `Gerador de Petição Simples` (agente) | `~/.claude/agents/` | aceite simples, agendamento, mutirão, escusa |
| `Gerador de Petição Médio` | `~/.claude/agents/` | aceite condicionado + proposta |
| `Gerador de Petição Complexo` | `~/.claude/agents/` | resposta a impugnação, contestação |
| `peticao-extrator` | `~/.claude/agents/` | extrai campos do processo |
| `peticao-identificador` | `~/.claude/agents/` | identifica tipo + subtipo a partir de texto |
| `peticao-montador` | `~/.claude/agents/` | preenche template com dados |
| `peticao-verificador` | `~/.claude/agents/` | confere CNJ, IDs, gênero do juiz, valor por extenso |
| `peticao-gerador-pdf` | `~/.claude/agents/` | converte MD → PDF timbrado |
| `Conferidor e Verificador de Petição` | `~/.claude/agents/` | qualidade pré-PDF |
| `orquestrador-automatico.sh` | `~/stemmia-forense/` | dispara o pipeline correto |

**Já tem 12 agentes que cobrem QUASE TUDO.** Falta só:
1. Detector da página de nomeação (passo 1 acima)
2. Banco SQLite de aprendizado de variáveis novas
3. Saída com rastreabilidade parágrafo→fonte

---

## Banco de dados para aprendizado contínuo

Estrutura proposta (SQLite simples, sem servidor):

```sql
-- ~/.claude/projects/-Users-jesus/db/aceite_aprendizado.db

CREATE TABLE situacao (
    id INTEGER PRIMARY KEY,
    descricao TEXT,                -- "ainda aguardando mutirão"
    primeira_ocorrencia DATE,
    n_ocorrencias INTEGER DEFAULT 1,
    decisao_padrao TEXT,           -- "informar pendência ao juízo"
    template_paragrafo TEXT,       -- texto a usar
    aprovado_em DATE,
    aprovado_por TEXT DEFAULT 'jesus'
);

CREATE TABLE processo_processado (
    cnj TEXT PRIMARY KEY,
    data_processamento DATE,
    tipo_aceite TEXT,
    honorarios REAL,
    local TEXT,
    data_limite DATE,
    situacoes_detectadas TEXT,     -- JSON com IDs de situacao
    petição_path TEXT,
    aprovada BOOLEAN
);
```

Toda vez que rodar o pipeline:
1. Procura situações conhecidas no `situacao`
2. Se aparece situação NOVA → pausa, mostra ao Jésus
3. Jésus aprova ou descarta
4. Se aprova → grava no banco com decisão padrão
5. Próximas vezes: aplica automaticamente

---

## Próximo passo concreto

**HOJE não dá para implementar tudo.** Dá para implementar Fase 1+2+3+6 com agentes existentes.

Precisa de **1 sessão dedicada** para juntar os 12 agentes existentes num pipeline novo `/aceite-novo` que:
- Recebe PDF
- Acha a nomeação
- Recorta
- Chama os agentes na ordem certa
- Devolve petição + checklist

Banco de aprendizado pode entrar na 2ª sessão.

---

## O que o Jésus precisa decidir

| Decisão | Opção A | Opção B | Quando decidir |
|---------|---------|---------|----------------|
| Detectar nomeação por regex ou por LLM? | regex (rápido, exato) | LLM (entende contexto) | antes de codar |
| Banco em SQLite ou JSON? | SQLite (busca rápida) | JSON (humano lê direto) | antes de codar |
| Pausar para confirmar variável nova ou só registrar? | pausar (controle) | só registrar (rapidez) | antes de codar |
| Saída em MD primeiro ou PDF direto? | MD (revisa antes) | PDF (1 passo) | antes de codar |

Recomendação minha: regex+LLM combinados, SQLite, pausar SEMPRE em variável nova, MD primeiro depois PDF.
