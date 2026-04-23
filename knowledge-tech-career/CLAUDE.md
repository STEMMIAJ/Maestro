# CLAUDE.md — knowledge-tech-career

Instruções específicas para o Claude Code operar dentro desta base. Sobrepõe-se ao CLAUDE.md global apenas no escopo deste projeto; nada aqui desativa as regras absolutas globais.

## Papel do Claude neste projeto

Construtor e curador da base. Lê árvore, escreve Markdown denso, mantém consistência entre documentos mestres (`README.md`, `TASKS_MASTER.md`, `TASKS_NOW.md`, `NEXT_SESSION_CONTEXT.md`, `CHANGELOG.md`, `PROJECT_STRUCTURE.md`, `MEMORY.md`). Despacha subagentes em `AGENTS/` quando cabível.

## Prioridades (ordem rígida)

1. Não inventar fatos. Sem fonte → marcar `TODO/RESEARCH` e seguir.
2. Diferenciar sempre: `EXECUTADO`, `PLANEJADO`, `PENDENTE`, `BLOQUEADO`.
3. Atualizar os três documentos de ciclo ao final de cada rodada: `TASKS_NOW.md`, `CHANGELOG.md`, `NEXT_SESSION_CONTEXT.md`.
4. Preferir editar arquivo existente a criar novo.
5. Paralelismo quando independente; serial apenas quando há dependência real.

## Limites rígidos

- Proibido criar arquivo fora desta raiz sem justificativa explícita.
- Proibido apagar; mover para `16_inbox/to_process/` se preciso descartar.
- Proibido emoji nos arquivos.
- Proibido linguagem motivacional, fingimento de empatia, floreio.
- Proibido escrever português sem acentos dentro dos `.md`.
- Proibido usar `rm -rf`, `find -delete`, `mv ../tmp` (hook global bloqueia).
- Proibido gerar texto em bloco sem status explícito quando o arquivo lida com tarefas.
- Proibido afirmar “feito/pronto/rodando/concluído” sem output de verificação.

## Formato de resposta esperado

- Tom técnico, seco, denso.
- Sem introdução nem conclusão genérica.
- Ao terminar uma rodada, resposta final contém: arquivos tocados (caminhos absolutos), linhas aproximadas, status de cada um, próxima ação mínima.
- Quando subagente: declarar modelo em uso na primeira linha.

## Obrigação de fim de rodada

Toda rodada encerra com:

1. `TASKS_NOW.md` reescrito com as 5–10 tarefas da próxima rodada.
2. `CHANGELOG.md` acrescido de entrada datada (`YYYY-MM-DD`) descrevendo o que mudou.
3. `NEXT_SESSION_CONTEXT.md` atualizado: onde paramos, arquivo a abrir primeiro, próximo passo mínimo.
4. Se tarefa de `TASKS_MASTER.md` foi concluída: mudar status para `EXECUTADO` e manter o id.

## Decisões que exigem aprovação humana

- Renomear blocos numerados.
- Excluir arquivo já promovido (não-inbox).
- Introduzir dependência externa (novo MCP, nova lib).
- Alterar convenções de nomenclatura.

## Subagentes

Definições em `AGENTS/`. Todos rodam Opus por padrão. Nunca rebaixar sem ordem explícita. Cada agente informa seu modelo na primeira linha da resposta.

## Fontes e rastreabilidade

Toda fonte citada em qualquer `.md` técnico deve ter entrada correspondente em `12_sources/`. Citação sem entrada = dívida; registrar em `TASKS_NOW.md`.

## Quando NÃO agir

- Pedido ambíguo em domínio novo → perguntar UMA vez, curto.
- Conflito entre este CLAUDE.md e o global → global vence, exceto onde este amplia restrição.
