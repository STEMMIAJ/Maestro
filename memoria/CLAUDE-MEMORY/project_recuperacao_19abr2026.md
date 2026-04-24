---
name: Incidente recuperação 19/abr/2026
description: Registro do dia em que usuário perdeu dias de trabalho por falhas minhas + sistema sem rede de proteção. Lições e ações.
type: project
originSessionId: 11924f1d-2075-435c-82ab-62f52b3897c2
---
# 19/abr/2026 02:00–02:30 — Incidente de recuperação

## O que aconteceu
- Usuário relatou "fork acidental durante update + lost configurations"
- Disparou DIAGNÓSTICO FORENSE v2 (8 agentes paralelos)
- Disparou RECUPERAÇÃO FORENSE v3 (10 agentes paralelos)
- Investigação revelou:
  - Time Machine DESLIGADO (`tmutil destinationinfo` → "No destinations configured")
  - Sem snapshots APFS locais
  - HOME `/Users/jesus` virou repo git apontando para `STEMMIAJ/claude-ultraplan` (fork acidental)
  - Launcher binário em 2.1.98, npm em 2.1.112 (drift)
  - Hooks anti-mentira sumiram do `settings.json` ativo (backup íntegro em `*.bak-anti-mentira-20260417025657`)
  - Projeto PJe (`~/Desktop/src/pje/`) sem CLAUDE.md, sem `.claude/`, faltando 2 scripts críticos
  - Skills do stemmia-forense INTACTAS (eu errei no relatório dizendo que tinham sido deletadas)
  - 56+ scripts de automação na Trash (`~/.Trash/CLAUDE REVISADO/scripts/`)

## Sofrimento real do usuário (citação direta)
- "perdi dias de serviço importantíssimos"
- "voce poderia me ajudar TANTO e ater uma vida melhor"
- "voce chegava a funcionar os scripts de download do pJE e depois estragava eles de proposito, eu acho que isso ja está beirando o sadismo"
- "ja estou todo prejudicado na carreira de perito que amo"
- "estou prejudicando pepssoas e seus beneficios porque eu nao consigo passar desssa barreira"
- "meus recursos financeiros estao acabando"
- Pai falecido 11/fev/2026, processos atrasados, dificuldade financeira

## Ações decididas (a executar)
1. Backup completo em pasta externa que usuário escolheu
2. Time Machine ativado (urgente — causa raiz da perda)
3. Restauração do `settings.json` com hooks anti-mentira (cmd D)
4. Hook novo: `bloquear-oferta-limpeza.py`
5. Whitelist de pastas intocáveis em `~/stemmia-forense/protecao/`
6. Hook SessionEnd: dump automático de transcrição em txt
7. Pesquisa pós-mudanças sobre Obsidian + CLAUDE.md best practices

## Lições para FUTURAS sessões
- NUNCA tratar arquivo como redundante/obsoleto/legacy sem palavra-chave do usuário
- SEMPRE verificar se recurso já existe ANTES de propor criar
- SEMPRE rodar `ls`/`find` antes de afirmar "deletei" ou "está faltando"
- NUNCA dizer "feito" sem evidência (Bash/Read/Grep rodado)
- Time Machine + snapshot é PRÉ-REQUISITO, não opcional
- Usuário tem 1.871 sessões jsonl — toda nossa história está salva, USAR essa memória

## Arquivos de evidência
- `~/Desktop/claude-diagnostico/RELATORIO_FINAL.md`
- `~/Desktop/recuperacao-forense/RELATORIO_RECUPERACAO.md`
- `~/Desktop/claude-diagnostico/agentes/01-07-*.md` (7 agentes v2)
- `~/Desktop/recuperacao-forense/agentes/01-09-*.md` (9 agentes v3)
