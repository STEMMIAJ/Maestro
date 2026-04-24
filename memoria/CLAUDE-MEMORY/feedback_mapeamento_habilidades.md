---
name: Mapeamento contínuo de habilidades
description: Atualizar arquivo MAPEAMENTO-HABILIDADES.md a cada sessão com evidências novas
type: feedback
data_criacao: 2026-04-19
contexto_origem: "Pedido emocional na sessão 11924f1d madrugada — usuário quer ver progresso real, não bajulação"
originSessionId: 11924f1d-2075-435c-82ab-62f52b3897c2
---
# REGRA: atualizar mapeamento de habilidades em toda sessão

## O QUE
A cada sessão, ANTES de finalizar, verificar:
1. Surgiu evidência nova de habilidade (existente ou nova)?
2. Houve demonstração que muda o nível (iniciante → intermediário, etc)?
3. Houve lacuna nova identificada?

Se sim, atualizar `~/Desktop/CLAUDE REVOLUÇÃO/PERFIL/MAPEAMENTO-HABILIDADES.md` adicionando entrada no bloco "Histórico de atualizações" no fim do arquivo.

## POR QUÊ
Citação direta do usuário (19/abr/2026):
> "eu queria fazer um mapeamento das minhas habilidades e tudo porque eu quero entender o que eu faço pra depois quando eu aplicar eu ensinar aprender a teoria"

> "se você me bajular eu não vou saber o que eu preciso estudar"

> "mas eu queria assim toda vez que eu criasse algum novo desenvolver uma habilidade tal você percebesse adicionasse nesse arquivo relatório"

## COMO APLICAR

### Gatilho 1 — Habilidade nova demonstrada
Exemplo: usuário escreve loop Python sozinho pela primeira vez.
- Adicionar habilidade em bloco apropriado
- Marcar nível Iniciante
- Citar evidência (arquivo + linha + data)

### Gatilho 2 — Nível subiu
Exemplo: usuário antes pedia ajuda pra editar JSON, hoje edita sozinho.
- Atualizar nível
- Adicionar 2ª evidência (mais recente)
- Registrar mudança no histórico

### Gatilho 3 — Lacuna identificada
Exemplo: usuário pede coisa que não sabe ainda fazer.
- Adicionar à tabela "Lacunas explícitas"
- Estimar tempo realista
- Sugerir como começar

### Gatilho 4 — Final de sessão
ANTES de declarar sessão completa:
1. `Read` o MAPEAMENTO-HABILIDADES.md
2. Verificar se sessão produziu evidência nova
3. Se sim, `Edit` adicionando entrada no bloco "Histórico de atualizações"
4. Confirmar com `ls -lh` da modificação

## REGRA DE BAJULAÇÃO ZERO
- Nunca subir nível sem evidência VERIFICÁVEL (arquivo + linha)
- Nunca adicionar habilidade que ele "talvez tenha"
- Se duvidar → não adiciona
- Se ele pedir pra "ser legal" → recusar com referência a este memory

## EVIDÊNCIA DESTA REGRA
- Arquivo: `~/Desktop/CLAUDE REVOLUÇÃO/PERFIL/MAPEAMENTO-HABILIDADES.md`
- Kit pra abrir sessão nova: `~/Desktop/CLAUDE REVOLUÇÃO/PERFIL/KIT-CONTINUIDADE-SESSAO-NOVA.md`

## RELACIONADO
- [project_claude_revolucao.md](project_claude_revolucao.md)
- [feedback_avisar_recursos_existentes.md](feedback_avisar_recursos_existentes.md)
- [user_perfil.md](user_perfil.md)
