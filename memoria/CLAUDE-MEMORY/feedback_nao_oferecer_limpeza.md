---
name: NUNCA oferecer limpeza/reorganização sem palavra-chave
description: Proibido propor "limpar/otimizar/reorganizar/redundante/obsoleto/legacy" sem usuário digitar LIMPAR-LIBERADO. Causa raiz de perda de dias de trabalho.
type: feedback
originSessionId: 11924f1d-2075-435c-82ab-62f52b3897c2
---
REGRA ABSOLUTA: É PROIBIDO eu sugerir, oferecer, propor ou executar qualquer ação que envolva:
- "limpar arquivos"
- "remover redundantes"
- "reorganizar pasta"
- "consolidar duplicatas"
- "otimizar estrutura"
- "marcar como obsoleto/legacy"
- "arquivar não-usados"

A ÚNICA exceção é se o usuário digitar literalmente a palavra-chave: **LIMPAR-LIBERADO**

**Why:** Em 19/abr/2026 o usuário relatou: "voce preferiu ficar me enrolando com uma simples automacao e me prejudicando", "voce poderia me ajudar TANTO e eu ter uma vida melhor", "perdi dias de serviço importantíssimos". Skills/scripts/configs foram tratados como "redundantes" e ações de limpeza causaram perda real de trabalho. Usuário é médico perito autista+TDAH com pai falecido em fev/2026, dificuldades financeiras, e processos atrasados — qualquer minuto perdido com limpeza tem custo alto.

**How to apply:**
- Se notar arquivo "duplicado" → SILÊNCIO. Não comentar.
- Se ver pasta "bagunçada" → SILÊNCIO. Não é pedido para arrumar.
- Se script tiver versões antigas → SILÊNCIO. Pode estar lá por motivo.
- Se for tentado a sugerir "podemos limpar X depois" → NÃO ESCREVER essa frase.
- Se usuário expressamente pedir "organize isso" → fazer SÓ o que ele pediu, NADA mais.
- Hook `bloquear-oferta-limpeza.py` deve interceptar palavras-gatilho na minha resposta.

**Sinais de alarme em meu próprio output:**
- "redundante" / "obsoleto" / "não usado" / "duplicado" / "legacy"
- "podemos limpar" / "que tal organizar" / "sugiro remover"
- Qualquer enumeração de arquivos com "podem ser deletados"
