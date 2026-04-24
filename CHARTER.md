# Maestro — Charter

## Missão em uma frase
Pipeline operacional de perícia médica judicial do Dr. Jesus: captura → análise → laudo → entrega, com rastreabilidade total e zero retrabalho.

## Quem usa
Dr. Jesus (perito médico judicial, CRM MG, TEA+TDAH). Usuário único inicialmente.

## O que é
Conjunto de agentes, scripts e fluxos que transformam um processo judicial (PJe/DataJud) em laudo pericial entregue, passando por: aceite, proposta de honorários, agendamento, exame, análise, redação, conferência e entrega assinada.

## O que NÃO é
- Não é dashboard web público
- Não é SaaS multiusuário
- Não é produto à venda (por enquanto)
- Não é substituto do perito — é amplificador cognitivo dele

## Sucesso = ?
Um laudo pericial completo, gerado pelo pipeline, entregue no PJe, sem intervenção manual fora dos pontos de decisão clínica do perito.

## Restrições
- Roda em macOS (Darwin 25.1.0)
- Base: `~/Desktop/STEMMIA Dexter/Maestro/`
- Python + Bash + Claude Code (Opus 4.7) + gh CLI
- PJe só acessado via Windows/Parallels quando houver captcha
- Sem custos mensais de SaaS (exceto Anthropic/Claude Code já contratado)

## Stakeholders
- **Dono:** Dr. Jesus
- **Executor:** Claude Code (sessões interativas)
- **Auditor externo:** desenvolvedor contratado para revisão (recebe pacote `AUDITORIA OPENCLAW`)

## Princípio-mestre
**Um sistema que não termina uma tarefa é pior que nenhum sistema.** Toda feature nasce com Definition of Done. Sem DOD, não começa.
