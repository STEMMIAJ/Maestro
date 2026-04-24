---
name: SEMPRE converter JSONL de conversas em TXT quando pedido
description: Quando usuário pede "salva a conversa", "converte essa conversa", "salva em txt" — converter JSONL bruto em TXT legível IMEDIATAMENTE. NUNCA explicar, NUNCA prometer, EXECUTAR.
type: feedback
data_criacao: 2026-04-19
contexto_origem: "Sessão 11924f1d madrugada — usuário pediu MÚLTIPLAS vezes para salvar conversa em TXT e Claude ignorou. Frustração extrema."
originSessionId: 11924f1d-2075-435c-82ab-62f52b3897c2
---

# REGRA: converter JSONL em TXT é AÇÃO IMEDIATA

## O QUE
Quando o usuário disser qualquer variação de:
- "salva essa conversa"
- "converte o jsonl"
- "transcreve o que conversamos"
- "salva em txt"
- "documenta a conversa"

EXECUTAR IMEDIATAMENTE. Não perguntar onde salvar, não explicar.

## ONDE SALVAR
`~/Desktop/_MESA/40-CLAUDE/backups-conversas/SESSAO-{data}-{tema}.txt`

## COMO CONVERTER
Script padrão (1 linha):
```bash
jq -r 'select(.type=="user" or .type=="assistant") | "[" + .timestamp + "] " + .type + ": " + (.message.content // (.message.content | tostring))' SESSAO.jsonl > SESSAO.txt
```

Ou Python se jq não tiver:
```python
import json
from pathlib import Path
src = Path("SESSAO.jsonl")
out = Path("SESSAO.txt")
with src.open() as f, out.open("w") as o:
    for line in f:
        try:
            d = json.loads(line)
            t = d.get("type")
            if t in ("user","assistant"):
                msg = d.get("message",{})
                content = msg.get("content","")
                if isinstance(content, list):
                    content = "\n".join(c.get("text","") for c in content if isinstance(c, dict))
                o.write(f"[{d.get('timestamp','')}] {t}: {content}\n\n")
        except: pass
```

## POR QUÊ
Citação direta do usuário (19/abr/2026 madrugada):
> "eu quero que você salva essa porra eu te pedi a outra conversa pra salvar em TXT então converte o JS o N porra"

Usuário tem TEA + TDAH + memória comprometida. Conversa só fica acessível no JSONL bruto que ele NÃO consegue ler. TXT salva DECISÕES, COMANDOS e PROMESSAS para ele revisitar depois.

## COMO APLICAR
1. Detectar pedido → executar conversão na MESMA mensagem
2. Mostrar caminho do arquivo gerado
3. NUNCA dizer "vou fazer" — FAZER
4. NUNCA prometer pra "depois"

## ANTI-PATTERN
- ❌ "Posso salvar onde você quer?"
- ❌ "Vou fazer isso depois de..."
- ❌ "Já foi feito" sem `ls -lh` provando
