# Projetos Externos — Infraestrutura

## Hosting — Nuvem Fácil

- **Provedor:** Nuvem Fácil
- **Tipo:** Hospedagem compartilhada
- **Uso:** Site stemmiapericia.com + arquivos públicos (laudos, petições para clientes)
- **Deploy:** Via FTP (senha atualizada 16/mar/2026)
- **Procedimento:** Subir arquivo via FTP → atualizar Planner com link

## Site — stemmiapericia.com

- **URL:** https://stemmiapericia.com
- **Conteúdo:** Página institucional da Stemmia Perícia Médica
- **Stack:** HTML/CSS estático
- **Atualizações:** Via FTP direto

## Bot Telegram

- **Username:** @stemmiapericia_bot
- **Chat ID:** 8397602236
- **Uso:** Notificações de movimentações processuais, alertas de prazo
- **Status:** Ativo

## N8N Self-Hosted

- **URL:** https://n8n.srv19105.nvhm.cloud
- **Uso:** Automações (análise pericial, pesquisador de produtos, monitor publicações)
- **Acesso:** Via MCP ou interface web
- **Limitação:** Workflows pesados travam no cloud — testar local primeiro

## Parallels (Windows)

- **Uso:** PJe (acesso com certificado A1), softwares Windows-only
- **Chrome PJe:** Perfil isolado, porta debug 9223
- **REGRA:** PJe SÓ no Windows/Parallels, NUNCA Mac Chrome
