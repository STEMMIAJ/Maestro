# PROMPT PARALELO — Dr. Jesus executa enquanto IA trabalha

Use este prompt em **OUTRA sessao/aba do Claude Code ou qualquer LLM generico**. Ele te guia passo a passo — abre links, fala exatamente onde clicar, o que copiar, onde colar.

## Como usar
1. Abra outra aba de Claude Code OU ChatGPT/Perplexity.
2. Cole este prompt inteiro.
3. Siga cada etapa. Cada uma leva 2-5 minutos.
4. No fim, volta para a sessao principal com os valores copiados.
5. Total estimado: **20-35 minutos** seu tempo ativo (pausas entre etapas permitem responder telefone/perito).

---

## PROMPT PARA COLAR

```
Voce e meu copiloto operacional. Eu, Dr. Jesus, preciso coletar 4 credenciais/decisoes em paralelo enquanto outra sessao do Claude trabalha. Me guie passo a passo. UMA etapa por vez. Sempre:
- Fale exatamente o site pra abrir.
- Fale exatamente o que clicar.
- Me avise quando o valor aparecer na tela para eu copiar.
- Me diga onde colar (um arquivo txt no Desktop chamado `credenciais-maestro-2026-04-23.txt`).
- Nao avance sem confirmacao.

Valores a coletar:

### [1] API key Anthropic (para scripts Python chamarem Haiku)
- URL: https://console.anthropic.com/settings/keys
- Login com a conta que o Dr. Jesus ja usa no Claude Code.
- Criar nova chave "Maestro-scripts".
- Copiar a chave (comeca com `sk-ant-api03-...`).
- Salvar em: `~/Desktop/credenciais-maestro-2026-04-23.txt` na linha "ANTHROPIC_API_KEY=..."

### [2] Bot Telegram
- Abrir Telegram no celular OU web (https://web.telegram.org).
- Buscar @BotFather.
- Enviar `/newbot`.
- Nome sugerido: "Maestro Stemmia Bot".
- Username sugerido: "maestro_stemmia_bot" (se nao estiver livre, tenta variacao).
- BotFather devolve um TOKEN (formato `123456:ABC-DEF...`).
- Copiar o TOKEN para o txt na linha "TELEGRAM_BOT_TOKEN=..."
- Depois, mandar `/start` para o proprio bot recem-criado.
- Abrir no navegador: https://api.telegram.org/bot<SEU_TOKEN>/getUpdates
- Procurar "chat":{"id": NUMERO  — copiar esse NUMERO.
- Salvar em: "TELEGRAM_CHAT_ID=..."

### [3] FTP nuvemhospedagem.com.br
- Abrir painel em: https://painel.nuvemhospedagem.com.br (ou similar, checar email de ativacao da conta).
- Logar com o email do Dr. Jesus.
- Procurar secao "FTP" ou "Gerenciador de Arquivos > Credenciais FTP".
- Anotar: host, usuario, senha (ou criar senha nova se nao lembrar), porta (normalmente 21 FTP ou 22 SFTP).
- Salvar em: "FTP_HOST=...", "FTP_USER=...", "FTP_PASS=...", "FTP_PORT=..."
- BONUS: testar se suporta `.htaccess` — na maioria dos planos compartilhados nuvemhospedagem suporta.

### [4] Decisao: restaurar ou comecar limpo no OpenClaw
- Contexto: ~/.openclaw ja existe com 200MB de estado (v2026.4.2, auth Anthropic OK, credencial WhatsApp, memoria main.sqlite).
- Opcao A (limpa): desinstalar, apagar ~/.openclaw, reinstalar do zero, reconfigurar tudo do Maestro.
- Opcao B (preserva): backup + desinstalar binario + reinstalar + restaurar credenciais mas memoria/flows ficam vazios.
- Opcao C (nao mexer): manter versao atual e apenas integrar com Maestro.
- Recomendacao da IA: B (backup tudo, reinstalar limpo, restaurar so auth Anthropic).
- **Decisao do Dr. Jesus:** A ou B ou C → salvar na linha "OPENCLAW_STRATEGY=..."

No fim: abrir ~/Desktop/credenciais-maestro-2026-04-23.txt e confirmar que tem 6 linhas preenchidas:
- ANTHROPIC_API_KEY=
- TELEGRAM_BOT_TOKEN=
- TELEGRAM_CHAT_ID=
- FTP_HOST=
- FTP_USER=
- FTP_PASS=
- FTP_PORT=
- OPENCLAW_STRATEGY=

Quando tiver os 8 valores, volta para a sessao principal do Maestro e diz: "tenho as credenciais em ~/Desktop/credenciais-maestro-2026-04-23.txt".

Me guie UMA etapa por vez. Comece pela [1].
```

---

## Observacao de seguranca

- O arquivo `credenciais-maestro-2026-04-23.txt` fica no Desktop **temporariamente**.
- Quando a IA principal ler, ela **move os valores para `.env`** em Maestro/ (fora do git) e **apaga o txt do Desktop**.
- NAO comitar no git. `.gitignore` do Maestro ja exclui `*.env`.
