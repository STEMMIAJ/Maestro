---
name: Monitor de Fontes de Intimações
description: Automação que varre AJ TJMG + AJG + DJEN + DJE-TJMG + DataJud em ~/Desktop/MONITOR-FONTES/ via launchd 3x/dia
type: project
originSessionId: a581928f-91fb-4807-a144-52c006ae766d
---
# MONITOR-FONTES

Sistema que consolida citações/intimações/nomeações das fontes onde o perito recebe trabalho.

## Estrutura
`~/Desktop/MONITOR-FONTES/`
- `README.md` — documento mestre detalhado (fontes, pastas, como rodar, troubleshooting)
- `scripts/` — orquestrador.py, consolidador.py, gerar_dashboard.py, alerta_telegram.py, abrir_chrome_debug.command
- `dados/por-fonte/{aj,ajg,djen,domicilio,datajud}.json` — saída bruta
- `dados/processos-consolidados.{json,csv}` — lista deduplicada por CNJ, ordem cronológica desc
- `dados/historico/YYYY-MM-DD.json` — snapshot diário do status por fonte
- `dashboard/index.html` — dashboard com cards, filtros por fonte, tabela
- `logs/orquestrador-YYYY-MM-DD.log`
- `config/launchd/com.stemmia.monitor-fontes.plist` → symlink em `~/Library/LaunchAgents/`

## Fontes automatizadas
| ID | Fonte | Script | Autenticação |
|----|-------|--------|--------------|
| aj | AJ TJMG | `~/stemmia-forense/src/pje/consultar_aj.py` | Chrome debug 9223 logado manualmente |
| ajg | AJG Justiça Federal | `consultar_ajg.py` | Chrome debug 9223 logado manualmente |
| djen | DJEN/Comunica PJe | `~/stemmia-forense/automacoes/hub.py --discovery-only` | Cadastro Comunica PJe |
| domicilio | DJE-TJMG (HTML) | `~/stemmia-forense/src/pje/monitor-publicacoes/dje_tjmg.py --dias 1 --json` | Nenhuma |
| datajud | DataJud CNJ | `hub.py --status-only` | API pública |

PJe Painel é manual (VidaaS A3 só no Windows/Parallels).

## Cron
launchd executa 07:00, 13:00, 19:00 via `com.stemmia.monitor-fontes`.
Verificar: `launchctl list | grep monitor-fontes`

## Antes de rodar manualmente
1. Duplo-click em `scripts/abrir_chrome_debug.command` — abre Chrome perfil dedicado na porta 9223
2. Logar em AJ TJMG e AJG
3. Chrome debug NÃO deve ser fechado (sessão vivida entre execuções)

Se AJ/AJG retornar erro de login, Telegram avisa para relogar.

## Alertas Telegram (chat_id 8397602236)
- Novos CNJs: envia lista com fonte e data
- Deslogado: alerta com caminho do .command

## Token Telegram
`~/.stemmia/credenciais.env` → `TELEGRAM_BOT_TOKEN=...`

## Testes
27 testes pytest em `scripts/test_*.py` cobrem consolidador, alerta, orquestrador.

## Status de execução
Em modo degradado (Chrome não logado / scripts opcionais ausentes), o sistema roda sem crash: fontes com erro ficam no snapshot com `status=erro`, consolidador só lê JSONs válidos, dashboard reflete o que chegou.
