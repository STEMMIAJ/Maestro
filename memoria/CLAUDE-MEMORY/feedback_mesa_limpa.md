---
name: Mesa limpa — NUNCA criar arquivos na raiz do Desktop
description: Regra crítica de acessibilidade — TDAH+autismo: bagunça na Mesa causa dano real (perda de foco, atraso, sobrecarga sensorial)
type: feedback
---

NUNCA criar, copiar ou salvar arquivos na raiz de ~/Desktop/.

**Why:** O usuário tem TDAH + autismo. Bagunça visual na Mesa causa sobrecarga sensorial, perda de foco e atraso real no trabalho. Isso não é preferência estética — é necessidade de acessibilidade.

**How to apply:**
- Ao criar .md, salvar DENTRO da subpasta do projeto (nunca na raiz da Mesa)
- Pesquisas de produto → dentro de `~/Desktop/Pesquisas Produtos/` ou pasta temática
- Petições e aceites → dentro da pasta do processo em `ANALISADOR FINAL/processos/[CNJ]/`
- Planos → `~/Desktop/Projetos - Plan Mode/`
- Backups automáticos → `~/Desktop/Projetos - Plan Mode/documentos-criados/YYYY-MM-DD/`
- Se precisar que o usuário veja algo rapidamente, informar o caminho — nunca copiar para a Mesa
- O hook `copiar-md-automatico.sh` foi corrigido em 2026-03-17 para NÃO copiar para a Mesa
