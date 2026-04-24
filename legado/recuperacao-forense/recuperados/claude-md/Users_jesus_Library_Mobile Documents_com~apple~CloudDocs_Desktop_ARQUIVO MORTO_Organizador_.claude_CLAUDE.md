# Organizador de Perícias — Instruções Locais (DEPRECADO)

> **AVISO:** Esta pasta está em ARQUIVO MORTO. O sistema ativo está em `~/Desktop/ANALISADOR FINAL/`.
> Use `/priorizar` no ANALISADOR FINAL para gerenciar processos.

## O que é esta pasta

Central de controle de 30 perícias judiciais do Dr. Jesus Eduardo Noleto da Penha (CRM/MG 92.148).

## Estrutura

- `STATUS.md` — Painel geral com TODOS os processos por categoria
- `processos/pericia-XX/` — Subpasta de cada perícia com FICHA.md
- `modelos/` — Templates de petições
- `pje-automatizado/` — Automação PJe

## DETECÇÃO AUTOMÁTICA DE INTENÇÃO

| O que o usuário diz | O que fazer |
|---------------------|-------------|
| "status", "painel", "como estão as perícias" | Ler e mostrar STATUS.md |
| "perícia X", "processo X", número de perícia | Abrir FICHA.md da perícia correspondente |
| "atualiza status da perícia X" | Editar STATUS.md e FICHA.md |
| "quais são urgentes", "prioridade" | Filtrar STATUS.md por urgência ALTA |
| "quantas perícias tenho", "listar" | Contar e listar por categoria |
| "próximo passo da perícia X" | Ler FICHA.md e indicar ação pendente |
| "analise esse processo" | Redirecionar para ~/Desktop/analisador de processos/ (skill /analisar) |

## Categorias (extraídas do STATUS.md)

- **PREVIDENCIÁRIA** — 13 processos (auxílio-doença, aposentadoria, BPC/LOAS)
- **INTERDIÇÃO/CURATELA** — 5 processos
- **ACIDENTE DE TRÂNSITO** — 5 processos
- **ERRO MÉDICO / SAÚDE** — 3 processos
- **SECURITÁRIA** — 2 processos
- **DANO MORAL / TRABALHISTA** — 2 processos

## Ao Atualizar Status

1. Editar a linha correspondente em `STATUS.md`
2. Editar `FICHA.md` na subpasta da perícia
3. Informar o que mudou

## Dados do Perito

- Nome: Jesus Eduardo Noleto da Penha
- CRM/MG: 92.148
- Cidade: Governador Valadares/MG

## Regras

- NÃO perguntar o que fazer — ler STATUS.md e AGIR
- Respostas compactas — tabelas quando possível
- Quando o usuário disser um número de perícia (ex: "perícia 17"), ir direto em `processos/pericia-17/FICHA.md`
- Se o usuário quiser ANÁLISE de processo (não apenas status), redirecionar para o analisador de processos
