# B1 — Resolucao: ANTHROPIC_API_KEY persistente no gateway OpenClaw

**Criado:** 2026-04-24 (sessao 4)
**Bloqueio origem:** HANDOFF-2026-04-23-SESSAO-02 secao 5, B1
**Estado:** plist proposto pronto; aplicacao depende de `launchctl` (DENY ate ordem explicita)

---

## Problema
`ANTHROPIC_API_KEY` foi setada via `launchctl setenv` na sessao 1. Isso e volatil: some no proximo reboot. Gateway OpenClaw para de chamar API ate re-setar manualmente.

## Solucao
Adicionar a chave dentro do bloco `<key>EnvironmentVariables</key>` no plist `~/Library/LaunchAgents/ai.openclaw.gateway.plist`. Persiste entre reboots, escopo so do usuario `jesus`.

## Diff vs original (2 linhas novas)
```
    <key>OPENCLAW_SERVICE_VERSION</key>
    <string>2026.4.2</string>
+   <key>ANTHROPIC_API_KEY</key>
+   <string>__ANTHROPIC_API_KEY_VALUE__</string>
    </dict>
```

Plist proposto completo: `Maestro/futuro/plist-gateway-proposto.plist` (placeholder no lugar do segredo).

---

## Procedimento manual (voce executa)

### 1. Backup
```sh
cp ~/Library/LaunchAgents/ai.openclaw.gateway.plist \
   ~/Library/LaunchAgents/ai.openclaw.gateway.plist.bak-pre-B1
```

### 2. Substituir placeholder e copiar
```sh
# Le valor do .env e gera plist final num temp file
KEY="$(grep '^ANTHROPIC_API_KEY=' "/Users/jesus/Desktop/STEMMIA Dexter/Maestro/.env" | cut -d= -f2-)"
sed "s|__ANTHROPIC_API_KEY_VALUE__|${KEY}|" \
    "/Users/jesus/Desktop/STEMMIA Dexter/Maestro/futuro/plist-gateway-proposto.plist" \
    > /tmp/ai.openclaw.gateway.plist.new

# Validar XML antes de instalar
plutil -lint /tmp/ai.openclaw.gateway.plist.new

# Instalar
mv /tmp/ai.openclaw.gateway.plist.new ~/Library/LaunchAgents/ai.openclaw.gateway.plist
chmod 600 ~/Library/LaunchAgents/ai.openclaw.gateway.plist
```

### 3. Recarregar gateway
```sh
launchctl unload ~/Library/LaunchAgents/ai.openclaw.gateway.plist
launchctl load   ~/Library/LaunchAgents/ai.openclaw.gateway.plist
```

### 4. Validar
```sh
# Esperar 2-3s pro gateway subir
sleep 3

# Verificar processo
launchctl list | grep ai.openclaw.gateway      # PID > 0 = OK

# Verificar gateway respondendo
openclaw status                                  # esperado: gateway ONLINE
openclaw doctor                                  # esperado: 0 erros
```

### 5. Limpar `launchctl setenv` volatil (opcional)
```sh
launchctl unsetenv ANTHROPIC_API_KEY
```
A nova fonte da chave passa a ser o plist persistente.

---

## Rollback
```sh
launchctl unload ~/Library/LaunchAgents/ai.openclaw.gateway.plist
mv ~/Library/LaunchAgents/ai.openclaw.gateway.plist.bak-pre-B1 \
   ~/Library/LaunchAgents/ai.openclaw.gateway.plist
launchctl load ~/Library/LaunchAgents/ai.openclaw.gateway.plist
```

---

## Por que NAO foi automatizado
PERMISSOES.md v2 deny:
```
Bash(launchctl load:*)
Bash(launchctl unload:*)
```
Para liberar, voce diz "ativa launchctl B1" em chat. Ai Claude executa passos 1-5 e atualiza este doc com timestamp + output de validacao.

---

## Validacao final esperada
```
$ openclaw status
gateway: ONLINE  port 18789  uptime XXs

$ openclaw doctor
✓ 0 errors, 1 warning (device antigo — nao bloqueante, ver B2)
```
