---
name: Verificar antes de declarar sucesso
description: NUNCA dizer "feito/pronto/corrigido" sem output de verificação na mesma resposta. Screenshot ou comando de check obrigatório.
type: feedback
originSessionId: 62a9a87e-5295-4503-9e05-03b88b768f76
---
NUNCA dizer "feito", "pronto", "corrigido", "atualizado" sem verificação comprovada na mesma resposta.

**Why:** Sessão Claude Grid (12/abr/2026) — declarei "ícone atualizado" 4+ vezes sem verificar. Ícone nunca mudou. Usuário perdeu 30+ minutos. Causa: cache agressivo do macOS ignorava cp + killall Dock.

**How to apply:**
- Mudança visual → screenshot via computer-use OU comando de verificação (ls -la, md5, defaults read)
- Mudança em arquivo → cat/head para confirmar conteúdo
- Mudança em Dock → `defaults read com.apple.dock persistent-apps | grep -A5 NomeApp`
- Mudança em ícone → `md5 Contents/Resources/applet.icns` + comparar com esperado
- Output de verificação DEVE aparecer na mesma resposta que declara sucesso
