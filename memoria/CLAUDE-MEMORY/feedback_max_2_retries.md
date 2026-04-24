---
name: Máximo 2 tentativas da mesma abordagem
description: Se falhou 2x com a mesma classe de solução, PARAR e mudar de estratégia. Diagnosticar causa raiz antes da 3ª tentativa.
type: feedback
originSessionId: 62a9a87e-5295-4503-9e05-03b88b768f76
---
Se uma abordagem falhou 2 vezes, NUNCA repetir uma 3ª vez. Mudar de estratégia completamente.

**Why:** Sessão Claude Grid (12/abr/2026) — tentei cp applet.icns + killall Dock ~5 vezes, todas falharam pelo mesmo motivo (cache do macOS). Gastei 30+ minutos repetindo a mesma falha. A solução era NSWorkspace API + nome novo do app.

**How to apply:**
1. Tentativa 1 falhou → tentar variação da mesma abordagem (ok)
2. Tentativa 2 falhou → PARAR. Diagnosticar causa raiz.
3. Formular hipótese sobre POR QUE falha, não apenas COMO corrigir
4. Buscar abordagem de classe diferente (ex: em vez de file copy, usar API do sistema)
5. Para ícones macOS especificamente: NSWorkspace.setIcon é a API oficial. Cache é vinculado ao bundle path — trocar nome do .app bypassa o cache.
