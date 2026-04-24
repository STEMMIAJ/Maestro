---
name: Executar .bat no Windows via Parallels sem computer-use
description: Comando único que faz o Parallels executar .bat dentro da VM Windows automaticamente, sem interação manual
type: reference
originSessionId: 7bf6c134-00e2-4615-a37b-b060d0cbda41
---
Para executar código dentro do Windows (Parallels) a partir do Mac sem SSH/WinRM/computer-use:

```bash
open -a "Parallels Desktop" /caminho/arquivo.bat
```

Parallels registra `.bat`/`.exe` via `com.microsoft.windows-executable` e executa direto na VM rodando. Output via shared folder `\\Mac\Home\...` aparece imediatamente no filesystem do Mac.

**Why:** Parallels Desktop Standard (sem Pro) não tem `prlctl exec`. SSH/WinRM/SMB fechados na VM por firewall. Única via programática para rodar código no Windows é o URL handler que Parallels registra para executáveis.

**How to apply:**
1. Criar `.bat` no Mac com saída para `\\Mac\Home\Desktop\arquivo-saida.txt` (=/Users/jesus/Desktop/).
2. `open -a "Parallels Desktop" /caminho/do.bat` — dispara execução na VM.
3. Ler saída de volta no Mac após alguns segundos. Validado 16/abr/2026 com `BUSCAR-PROCESSOS-WIN.bat` (gerou txt em 15s).

**Pré-requisitos:**
- VM rodando (`prlctl list -a`).
- Shared Folders: `ShareUserHomeDir=1` no `config.pvs` (padrão do Parallels).
- Parallels Tools instalado no Windows guest.

**Caminho do prlctl (Standard):** `/Applications/Parallels Desktop.app/Contents/MacOS/prlctl`.
Standard suporta apenas: `list`, `start/stop`, `send-key-event`, `capture`. NÃO suporta `exec`/`enter`.
