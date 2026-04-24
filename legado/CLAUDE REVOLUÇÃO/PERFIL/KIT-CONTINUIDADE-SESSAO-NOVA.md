# Kit de Continuidade — para abrir sessão nova e pedir análise de perfil

**Como usar:** copie o bloco "PROMPT" abaixo, cole numa sessão nova do Claude Code. Ele vai ler tudo o que está referenciado e produzir a análise de perfil.

---

## PROMPT (copie tudo até o fim do bloco)

```
Quero que você faça uma análise IMPARCIAL e TÉCNICA do meu perfil profissional.

Não me bajule. Se eu não sei algo, me diga. Se eu domino algo, me dê EVIDÊNCIA exata (arquivo, data, comando que prova).

Antes de responder, leia em ordem:

1. CONTEXTO BASE
- ~/.claude/CLAUDE.md
- ~/.claude/projects/-Users-jesus/memory/MEMORY.md
- ~/.claude/projects/-Users-jesus/memory/user_perfil.md
- ~/.claude/projects/-Users-jesus/memory/project_claude_revolucao.md

2. EVIDÊNCIA HISTÓRICA
- ~/Desktop/CLAUDE REVOLUÇÃO/RELATORIO-FINAL-19abr2026.md (relatório da sessão de criação)
- ~/Desktop/CLAUDE REVOLUÇÃO/PERFIL/MAPEAMENTO-HABILIDADES.md (mapeamento contínuo)
- ~/Desktop/DIARIO-PROJETOS.md (histórico de projetos)
- Listar conteúdo de ~/.claude/agents/ (76 agentes que criei)
- Listar conteúdo de ~/.claude/skills/ (38 skills que criei ou customizei)
- Listar conteúdo de ~/stemmia-forense/src/pje/ (24 scripts PJe)
- Listar conteúdo de ~/.claude/projects/-Users-jesus/memory/ (67 memórias)

3. CONVERSA-FONTE (longa, leia se precisar verificar afirmação)
- ~/.claude/projects/-Users-jesus/11924f1d-2075-435c-82ab-62f52b3897c2.jsonl

4. PRODUZA o relatório SEGUINDO ESTE FORMATO EXATO:

# Análise de Perfil — Dr. Jésus Penna Noleto
Data: [hoje]
Avaliador: Claude [versão]

## 1. Identidade profissional (1 frase)
"Você é [...]"

## 2. Habilidades MAPEADAS (com evidência)
Para cada habilidade:
- Nome da habilidade
- Nível: iniciante / intermediário / avançado
- Evidência objetiva (arquivo + data + o que demonstra)
- Comparação com mercado (júnior/pleno/sênior em qual cargo)

## 3. O que VOCÊ AINDA NÃO sabe (lacunas)
- Lista honesta com prioridade
- Tempo realista para cobrir cada uma

## 4. Trajetória de aprendizado observada
- O que aprendeu primeiro
- O que aprendeu por último
- Padrão de aprendizado dele (reverse-engineering, exemplo-primeiro, etc)

## 5. Próximas habilidades RECOMENDADAS
- 3 habilidades que dariam maior salto
- Por que essas 3
- Como começar amanhã

## 6. Carreiras possíveis (com seu perfil)
- Lista de cargos REAIS de mercado que cabem no perfil dele
- Com salário mediano BR (se dado disponível)

## 7. O que NÃO dizer
- Erros comuns que outros conselheiros cometem com perfil dele
- Ex: "vire dev full-stack" → não, ele já é arquiteto vertical

REGRAS DA ANÁLISE:
- ZERO bajulação
- TODA afirmação tem evidência (arquivo + linha)
- Se duvidar, dizer "não tenho evidência suficiente"
- Tom seco, técnico, sem disclaimers
- Português com acentos
```

---

## Por que esse formato

- Garante que outra sessão tem TUDO que precisa
- Não depende de você ficar relembrando contexto
- Outras sessões não têm a memória desta — então o prompt carrega elas
- O formato fixo evita análise vaga

---

## Quando usar

1. A cada **30 dias** — pra ver evolução real
2. Quando **terminar** habilidade nova
3. Quando **dúvida** sobre próximo passo de carreira
4. Antes de **decisão grande** (mudar de área, parar perícia, etc)

---

## Onde guardar resultado

A análise gerada deve ser salva em:
`~/Desktop/CLAUDE REVOLUÇÃO/PERFIL/ANALISES/[data]-analise-perfil.md`

Mantém histórico — você compara meses e vê crescimento.
