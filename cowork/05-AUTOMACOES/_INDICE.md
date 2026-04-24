# Índice de Automações — STEMMIA Dexter

Atualizado: 2026-04-20. Referência rápida. Detalhes em `ROADMAP-AUTOMACOES.md`.

| Nome | Tipo | Status | O que faz | Dispara quando |
|---|---|---|---|---|
| `/novo-caso <numero>` | slash-command | proposto | Cria pasta do caso a partir de `_TEMPLATE-CASO/`, popula `FICHA.json` com dados do processo | Usuário digita comando no chat |
| `/peticao <tipo>` | skill | proposto | Lê `FICHA.json` + template da petição + produz MD timbrado em `peticoes-geradas/` | Usuário digita comando |
| `/laudo` | skill | proposto | Inicia ou continua laudo usando template por CID e dados da `FICHA.json` | Usuário digita comando |
| `/intimacao` | skill | proposto | Triagem de intimação do PJe: classifica, extrai prazo, propõe ação | Usuário digita comando ou cola texto |
| `/arquivar <numero>` | slash-command | proposto | Move caso encerrado de `01-CASOS-ATIVOS/` para `07-ARQUIVO/YYYY/` e atualiza índice | Usuário digita comando |
| `/dashboard` | slash-command | proposto | Imprime status compacto de casos ativos, prazos, pendências | Usuário digita comando |
| `post-write-peticao` | hook (PostToolUse) | proposto | Dispara agente verificador automaticamente após gravar arquivo em `peticoes-geradas/` | Write em path `**/peticoes-geradas/*.md` |
| `post-write-inbox` | hook (PostToolUse) | proposto | Classifica documento recém-caído em `INBOX/` (intimação, laudo externo, exame, outro) | Write em path `**/INBOX/*` |
| `resumo-prazos-8h` | cron/launchd | proposto | Envia ao Telegram os prazos do dia a partir do banco de casos ativos | Diário 08:00 |
| `extrator-padroes` | agente semanal | proposto | Lê casos encerrados na semana, extrai padrões, sugere atualização de templates | Domingo 22:00 |
| `voice-to-ficha` | skill + script | proposto (extra) | Transcreve ditado clínico e popula `FICHA.json` durante exame físico | Usuário inicia sessão de ditado |
| `ocr-watchdog-inbox` | launchd + script | proposto (extra) | OCR automático de PDFs escaneados que caem em `INBOX/` | fsevents em `INBOX/` |
| `timeline-global` | script | proposto (extra) | Gera timeline HTML/D3 de todos os casos (datas-chave por caso) | Manual ou cron semanal |
| `comparador-laudo-processo` | agente | proposto (extra) | Checa contradições entre laudo gerado e peças do processo | Pós geração de laudo |
| `calendar-prazos-cnj` | script + MCP Google Calendar | proposto (extra) | Cria eventos no Calendar a partir de prazos detectados | Novo prazo cadastrado |
| `modo-ferias` | slash-command | proposto (extra) | Consolida todos os casos, gera resumo, delega/agenda pendências antes de viagem | Usuário digita `/ferias <data>` |
| `modo-reentrada` | slash-command | proposto (extra) | Após pausa, lê diário + casos ativos + último JSONL e produz briefing de onde parou | Usuário digita `/reentrada` |

Legenda de status: proposto | em implementação | ativo | deprecated.
