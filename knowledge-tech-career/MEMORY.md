# MEMORY.md — knowledge-tech-career

Memória estável do projeto. Muda devagar. Não é log de sessão (isso vai em `15_memory/daily/`) nem decisão pontual (`15_memory/decisions/`). É o porquê da base existir e como ela se mantém coerente no tempo.

## Visão de longo prazo

Transformar o estudo desordenado de TI + dados em saúde + IA em uma base Markdown linear, consultável por agente, que sobrevive à memória comprometida do usuário. O teste de sucesso: em 18 meses, retomar qualquer bloco sem reler histórico — só `NEXT_SESSION_CONTEXT.md` + arquivo-alvo bastam.

Objetivos finais rastreáveis:

- Mapa de carreiras TI com posicionamento atual do usuário e três próximos passos realistas.
- Skill matrix viva com evidências (projetos, certificações, artefatos).
- Biblioteca de prompts, scripts e padrões reutilizáveis para perícia + IA.
- Ponte formal entre perícia judicial e engenharia de dados/software.

## Princípios de organização

1. **Blocos numerados são estáveis.** Nunca renomear sem aprovação. Renumerar = quebrar índices de agentes.
2. **Conteúdo cru entra só por `16_inbox/`.** Promoção para bloco numerado é decisão registrada em `15_memory/decisions/`.
3. **Um assunto = um arquivo.** Arquivos longos fragmentam em subarquivos; não virar monólito.
4. **Status explícito.** Todo item acionável traz `EXECUTADO|PLANEJADO|PENDENTE|BLOQUEADO` e data.
5. **Fonte obrigatória.** Afirmação técnica sem fonte = `TODO/RESEARCH` até ser fechado.
6. **Markdown puro.** Sem frameworks, sem plugins obrigatórios. Wikilinks são opcionais.
7. **Reversibilidade.** Nenhuma ação destrói histórico — Git + `CHANGELOG.md` garantem rollback.

## Relação entre estudo formal, uso prático e automação

A base opera em três camadas que se realimentam:

- **Estudo formal** (`01`–`08`, `10`): teoria, roadmap, certificações. Entrada: livros, docs oficiais, cursos. Saída: notas estruturadas, glossário, mapas mentais textuais.
- **Uso prático** (`09`, `11`, `13`): aplicação na perícia e no mapeamento pessoal. Entrada: casos reais, gaps identificados. Saída: relatórios, decisões, evidências de habilidade.
- **Automação** (`14`, `15`): prompts, scripts, pipelines. Entrada: repetição detectada nas duas camadas acima. Saída: artefato reutilizável que reduz o custo cognitivo de rodadas futuras.

Regra: nenhum item vira automação antes de aparecer ao menos duas vezes no uso prático. Evita arquitetar solução para problema que não existe.

## Integração com o ecossistema Dexter

- Raiz: `~/Desktop/STEMMIA Dexter/`.
- Git do Dexter versiona esta pasta como subdiretório.
- Skills do usuário (`~/.claude/skills/`) e hooks globais (`~/.claude/hooks/`) aplicam-se aqui.
- `PYTHON-BASE` é referência obrigatória para qualquer script em `14_automation/scripts/`.
- Mapa mestre de perícias (`~/.claude/docs/SISTEMA-PERICIAS-MAPA-MESTRE.md`) é vizinho, não pai — esta base não descreve o sistema pericial, descreve o conhecimento que o alimenta.

## Contratos permanentes

- Nomes de pasta/arquivo sem acento, sem espaço, sem cedilha.
- Português correto com acentos dentro dos `.md`.
- Nada de emoji.
- Nada de opinião sem fonte.
- Toda rodada termina com `TASKS_NOW.md` + `CHANGELOG.md` + `NEXT_SESSION_CONTEXT.md` atualizados.
