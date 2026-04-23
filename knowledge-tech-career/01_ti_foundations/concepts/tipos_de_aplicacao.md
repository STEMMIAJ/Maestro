---
titulo: "Tipos de aplicação"
bloco: "01_ti_foundations/concepts"
tipo: "conceito"
nivel: "iniciante"
versao: 0.1
status: "rascunho"
ultima_atualizacao: 2026-04-23
nivel_evidencia: "B"
tempo_leitura_min: 4
---

# Tipos de aplicação

Aplicação (ou *app*) = software voltado a resolver tarefa específica do usuário final ou de outro sistema. Classificação por forma de execução e interface:

## Desktop

Roda localmente no sistema operacional (macOS, Windows, Linux). Interface gráfica nativa (GUI). Não precisa navegador. Exemplo: Microsoft Word, Pages, Assinador CNJ (`pjeoffice-pro`), Obsidian.

Vantagem: acesso total ao hardware e sistema de arquivos. Desvantagem: precisa instalar e atualizar em cada máquina.

## Web

Roda no servidor; usuário acessa via navegador. Não instala nada (além do browser). Exemplo: PJe, Gmail, Planner, stemmia.com.br.

Subtipos:
- **SPA (Single Page Application)** — carrega HTML/JS uma vez, depois só troca dados via API (Gmail, Notion).
- **MPA (Multi Page Application)** — cada clique recarrega página inteira (PJe clássico).

## Mobile

Otimizada para smartphone/tablet. Duas variantes:
- **Nativa** — escrita para iOS (Swift) ou Android (Kotlin/Java). WhatsApp, app do Banco.
- **Híbrida/cross-platform** — código único para ambos via React Native, Flutter. Menos performance, mais velocidade de desenvolvimento.

## CLI (Command Line Interface)

Não tem janela; opera no terminal. Entrada por argumentos/stdin, saída por stdout. Exemplo: `git`, `ffmpeg`, `curl`, `python`, `claude`.

Vantagem: scriptável, composta por *pipes* (`cmd1 | cmd2`), essencial para automação. Usada intensivamente por perito que roda OCR em lote, converte PDF, gera hash de laudo.

## Daemon / serviço

Processo que roda em segundo plano, sem interface, continuamente. Inicia no boot. Exemplo: servidor web Nginx, banco PostgreSQL, launchd no macOS, MCP server do Claude.

No Unix chama-se *daemon* (com `d` no final: `sshd`, `httpd`). No Windows, *service*. No macOS usa `launchd` com arquivos `.plist`.

## Script

Programa curto, interpretado (não compilado), geralmente para automação pontual. Exemplo: `monitorar_movimentacao.py`, shell script `_sweep.sh`, `.bat` para Parallels.

Diferença para CLI: CLI é ferramenta de propósito geral (reutilizável); script é receita específica feita por você para resolver um caso.

## Por que importa para o perito

- Saber que tipo de aplicação você está usando define onde os dados ficam (local = desktop/CLI; remoto = web/mobile SaaS) — afeta cadeia de custódia.
- Automação pericial usa CLI + script + daemon. Monitor de processos é daemon agendado (launchd).
- Perícia em app mobile exige entender se é nativa (extração por ADB/iOS forensics) ou híbrida (código é JavaScript inspecionável).

## Referências

- [TODO/RESEARCH: citar Apple Developer docs sobre launchd vs background app].
