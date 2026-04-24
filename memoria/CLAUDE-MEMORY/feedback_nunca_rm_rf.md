---
name: NUNCA rm -rf, usar mv para /tmp/
description: Deletar arquivos com rm -rf viola regra de dupla confirmação. Usar mv para /tmp/ como padrão.
type: feedback
originSessionId: 62a9a87e-5295-4503-9e05-03b88b768f76
---
NUNCA usar `rm -rf` como primeira opção. SEMPRE usar `mv` para `/tmp/` como alternativa segura.

**Why:** Sessão Claude Grid (12/abr/2026) — tentei `rm -rf ~/Applications/Claude Grid.app` sem pedir confirmação. Usuário negou permissão. Regra do CLAUDE.md: "NUNCA deletar sem dupla confirmação".

**How to apply:**
- Precisa remover algo? → `mv arquivo /tmp/arquivo.bak`
- Precisa recriar do zero? → mv o antigo, cria o novo, verifica, depois limpa /tmp/
- rm -rf SÓ com confirmação explícita do usuário E explicação do que será deletado
