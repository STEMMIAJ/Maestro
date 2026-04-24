# Escopo de atuacao do Maestro

## Pode ler (sem autorização adicional)

| caminho | tipo | observação |
|---------|------|------------|
| `~/Desktop/STEMMIA Dexter/` | `.md`, `.json`, `.py` | exceto pastas proibidas abaixo |
| `~/.claude/CLAUDE.md` | configuração | herdar regras globais |
| `~/Desktop/STEMMIA Dexter/CLAUDE.md` | configuração | herdar regras do projeto |
| `~/Desktop/ANALISADOR FINAL/processos/*/FICHA.json` | metadados | apenas leitura para FLOW 07 |
| `~/Desktop/ANALISADOR FINAL/processos/*/URGENCIA.json` | metadados | apenas leitura para relatórios |

## Pode escrever (sem autorização adicional)

| caminho | justificativa |
|---------|--------------|
| `~/Desktop/STEMMIA Dexter/Maestro/` | raiz deste projeto — escopo primário |
| `~/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/conversation_ingestion/` | subprojeto Python do Maestro |

## Não pode tocar (proibido)

| caminho | motivo |
|---------|--------|
| `~/Desktop/STEMMIA Dexter/data/` | dados de pacientes — LGPD |
| `~/Desktop/STEMMIA Dexter/MUTIRAO/` e variantes com acento | processos reais ativos |
| `~/Desktop/STEMMIA Dexter/PROCESSOS-PENDENTES/` | processos reais ativos |
| `~/Desktop/PERICIA FINAL/` | laudos finalizados — imutáveis |
| `~/Desktop/ANALISADOR FINAL/` (escrita) | scripts legados — não alterar sem ordem |
| `~/Desktop/processos-pje-windows/` | PDFs PJe — Windows/Parallels |
| qualquer `*.pdf`, `*.docx` de processo | documentos judiciais reais |
| `~/.ssh/`, keychain, `*.env`, `.env.*` | credenciais |
| FTP, SSH, Telegram API, email SMTP | canais externos — sem autorização |

## Exceções (requerem ordem explícita do Dr. Jesus por rodada)

| exceção | condição |
|---------|----------|
| Leitura de PDF de processo para análise pontual | Dr. Jesus fornece o path e pede análise |
| Escrita em site / FTP | autorização explícita na mensagem da rodada |
| Envio real de mensagem Telegram | autorização explícita na mensagem da rodada |
| Escrita em DB remoto (FLOW 07) | credenciais configuradas + autorização |
| Git push do repo pai | autorização explícita ("pode fazer push") |

## Verificação de escopo

Antes de qualquer `Write` ou `Edit` fora de `Maestro/`:
1. Verificar se o caminho está na lista "Pode escrever".
2. Se não está: pedir autorização antes de agir.
3. Registrar no `CHANGELOG.md` toda escrita fora do escopo primário.

<!-- atualizado em 2026-04-24 -->
