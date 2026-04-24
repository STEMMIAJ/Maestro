---
name: PJe só no Windows/Parallels
description: Dr. Jesus usa PJe EXCLUSIVAMENTE no Windows via Parallels Desktop — NUNCA tentar Mac Chrome
type: feedback
---

PJe é acessado EXCLUSIVAMENTE pelo Chrome no Windows 11 dentro do Parallels Desktop.
NUNCA sugerir login no Mac Chrome. NUNCA tentar abrir PJe no Mac.

**Why:** Usuário ficou extremamente frustrado quando tentei usar Mac Chrome para PJe. Ele já estava logado no Windows e perdeu tempo com abordagem errada.

**How to apply:** 
- Para automação PJe: conectar ao Chrome Windows via CDP (IP 10.211.55.3, porta 9222) OU usar computer-use no Parallels
- Se CDP não estiver ativo no Windows: pedir ao usuário para rodar `start chrome --remote-debugging-port=9222` no Windows
- Parallels Desktop edition normal NÃO tem `prlctl exec` — não tentar
