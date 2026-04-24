# OpenClaw — Dashboard

## Visao geral
`openclaw dashboard` abre a **Control UI** do Gateway local usando o token de autenticacao ativo. Nao e um comando de metricas proprio: serve para lancar a UI web que acompanha o Gateway (hospedada pelo proprio servico, normalmente em loopback). Em runs com SecretRef nao resolvido, imprime uma URL nao-tokenizada e orientacao de remediacao em vez de expor segredo.

## Comando e opcoes
```bash
openclaw dashboard            # resolve token e abre no browser padrao
openclaw dashboard --no-open  # imprime a URL sem abrir
```

Notas:
- `dashboard` resolve SecretRefs de `gateway.auth.token` quando possivel.
- Para tokens gerenciados por SecretRef (resolvidos ou nao), imprime/copia/abre uma URL nao-tokenizada, evitando vazar secret em terminal, clipboard ou argv do browser.
- Se o SecretRef estiver indisponivel no path atual, o comando nao invalida a saida: mostra guidance explicito ao inves de colar placeholder invalido.

## Exemplos praticos
```bash
# Fluxo tipico: subir gateway e abrir dashboard
openclaw gateway start
openclaw dashboard

# CI/headless: so imprime URL
openclaw dashboard --no-open

# Inspecao profunda (combina com status e logs)
openclaw status --all
openclaw logs --follow
```

## Superficies visiveis na UI
A Control UI expoe (entre outros, conforme o Gateway que esta rodando):
- Overview de sessoes ativas, canais configurados e status de agentes.
- Painel de cron jobs e tasks em execucao (mesma informacao de `openclaw tasks list`).
- Health do Gateway (equivalente a `openclaw health`).
- Controle de modelos/providers (semelhante a `openclaw models status`).

Paineis exatos dependem de plugins instalados (cada plugin pode registrar suas proprias rotas HTTP).

## Relacao com Maestro
- Dashboard do OpenClaw = visao tecnica local em loopback para inspecao rapida de Gateway e agentes.
- Dashboard externo (ex.: stemmia.com.br) permanece separado, focado em visao pericial para o Dr. Jesus.
- Se o Maestro subir OpenClaw como servico local, `openclaw dashboard --no-open` pode entregar uma URL fixa para bookmark no navegador principal do Mac.

## Referencia
- Arquivo fonte: `docs/cli/dashboard.md`.
- Tambem citado em `docs/cli/index.md` (secao `dashboard`).
- Commit: `35ec4a9991`.
