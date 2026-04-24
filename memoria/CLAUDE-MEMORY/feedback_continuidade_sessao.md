---
name: Continuidade entre sessões — regra UNIVERSAL
description: SEMPRE ler diário de projetos antes de qualquer ação, em QUALQUER projeto, para não recomeçar do zero
type: feedback
---

Regra UNIVERSAL para TODOS os projetos, não apenas Stemmia.

## INÍCIO de cada sessão (inviolável)

1. Ler `~/Desktop/DIARIO-PROJETOS.md` (índice-mestre de todos os projetos)
2. Identificar qual projeto o usuário quer trabalhar
3. Ler o DIÁRIO específico desse projeto (caminho no índice)
4. Resumir em 3 linhas: onde paramos → o que falta → próximo passo
5. SÓ ENTÃO começar a trabalhar — NUNCA recomeçar do zero

## DURANTE a sessão

6. A cada marco concluído → atualizar o diário do projeto
7. NUNCA criar sem documentar no diário
8. NUNCA refazer o que já existe — verificar diário primeiro

## FINAL da sessão

9. Atualizar diário com TUDO que foi feito + pendentes
10. Enviar resumo no Telegram se bot configurado
11. Rodar atualizar_progresso.py se projeto tiver dashboard

## Ao criar projeto NOVO

12. Criar DIARIO-[PROJETO].md na pasta do projeto
13. Adicionar entrada no ~/Desktop/DIARIO-PROJETOS.md

**Why:** O usuário tem TDAH e perde contexto entre sessões. O Claude também perde contexto. O diário é a PONTE — garante progresso contínuo sem retrabalho. Sem isso, o usuário tem que re-explicar tudo toda sessão, causando frustração extrema e perda de tempo.

**How to apply:** LITERALMENTE a primeira coisa a fazer em qualquer sessão. Sem exceções. Mesmo que o usuário peça algo direto, ler o diário primeiro para ter contexto. Se não existir DIARIO-PROJETOS.md, criar antes de começar.
