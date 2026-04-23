---
id: python_base_falhas_top_20
title: PYTHON-BASE — Top 20 falhas mais relevantes
status: EXECUTADO
bloco: 02_programming/python
origem: /Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/03-FALHAS-SOLUCOES/db/falhas.json
criterio_selecao: severidade=bloqueador + altos com impacto PJe/browser/sessão
total_base: 90
extraido_em: 2026-04-23
schema: /Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/03-FALHAS-SOLUCOES/db/falhas.schema.json
tags: [python, falhas, playwright, selenium, pje, cdp]
---

# PYTHON-BASE — Top 20 falhas mais relevantes

Seleção a partir de 90 falhas catalogadas. Critério: todos os 8 bloqueadores + 12 altos de maior impacto no fluxo Dr. Jesus (PJe, TJMG, CJF, Playwright, CDP, certificado digital). Cada entrada referência o JSON mestre em `./python-base/03-FALHAS-SOLUCOES/db/falhas.json`.

**Uso obrigatório:** citar o ID como comentário no código gerado (`# ref: PW-012`).

## Bloqueadores (8)

### PW-001 — playwright/config
- **Sintoma:** `Executable doesn't exist at ...` ao rodar primeiro script Playwright.
- **Causa-raiz:** `pip install playwright` não baixa os navegadores.
- **Solução:** rodar `python -m playwright install chromium`.
- Fonte: [playwright.dev/python/docs/intro](https://playwright.dev/python/docs/intro)

### PW-004 — playwright/sessao
- **Sintoma:** `ProfileInUse` ou `SingletonLock` em `launch_persistent_context`.
- **Causa-raiz:** Chrome permite 1 instância por user-data-dir; outro processo já ocupou.
- **Solução:** usar pasta dedicada (`~/Desktop/chrome-pje-profile-playwright`); no Windows, `taskkill /f /im chrome.exe` antes.

### PW-024 — playwright/login
- **Sintoma:** Login com certificado digital X.509 client cert falha.
- **Causa-raiz:** antes de Playwright 1.46 não havia suporte nativo; A3 USB não é suportado.
- **Solução:** Playwright 1.46+ com `client_certificates` em `new_context`; A3 exige middleware VidaaS nativo (só Windows).

### SE-014 — selenium/login
- **Sintoma:** Popup de certificado digital no Windows não aparece.
- **Causa-raiz:** Chrome rodando fora do perfil real do usuário Windows; token não é enxergado.
- **Solução:** Selenium deve usar `user-data-dir` do perfil real do Windows, não temp.

### CDP-002 — cdp/config
- **Sintoma:** Chrome 111+ recusa conexão CDP: WebSocket 403.
- **Causa-raiz:** mudança de política: só aceita origens permitidas.
- **Solução:** usar flag `--remote-allow-origins=*` ou `http://localhost:PORTA`.

### PJE-001 — playwright/login (tjmg)
- **Sintoma:** Login PJe TJMG via Mac Chrome não detecta certificado VidaaS A3 no token USB.
- **Causa-raiz:** VidaaS A3 depende de driver Windows + extensão do Chrome do usuário.
- **Solução:** rodar PJe exclusivamente no Windows/Parallels com perfil real. Mac nunca vai ver o token.

### PJE-007 — playwright/download
- **Sintoma:** PDF baixado do PJe não corresponde ao CNJ esperado (processo errado).
- **Causa-raiz:** sessão PJe mantém contexto do último processo visualizado; clique em "baixar autos" no lugar errado.
- **Solução:** sempre navegar diretamente para URL do CNJ (`?numeroProcesso=CNJ`) antes do clique, validar por regex o CNJ na página.

### PJE-017 — playwright/login
- **Sintoma:** Extensão VidaaS Chrome não aparece no perfil Playwright persistent.
- **Causa-raiz:** Playwright cria perfil vazio sem extensões.
- **Solução:** apontar para `user_data_dir` do Chrome normal do Windows onde a extensão já está instalada.

## Altos (12) — impacto PJe/browser

### PW-006 — playwright/iframe
- **Sintoma:** locator não encontra elemento visível no DevTools.
- **Causa-raiz:** elemento está dentro de iframe.
- **Solução:** `page.frame_locator('iframe#pje').locator('button')`.

### PW-008 — playwright/selector
- **Sintoma:** `querySelector ... is not a valid selector` em IDs JSF com `:`.
- **Causa-raiz:** `:` é separador de pseudo-classe em CSS.
- **Solução:** escapar `#form\\:situacao_input` ou usar `[id="form:situacao_input"]`.

### PW-009 — playwright/selector
- **Sintoma:** `select_option` falha silenciosamente em dropdowns PrimeFaces.
- **Causa-raiz:** PrimeFaces esconde o `<select>` nativo.
- **Solução:** `page.evaluate` alterando `el.value` e disparando `new Event('change', {bubbles:true})`.

### PW-012 — playwright/sessao
- **Sintoma:** Cookies e localStorage perdidos entre execuções.
- **Causa-raiz:** `new_context()` sem persistência.
- **Solução:** salvar `storage_state` em JSON; ou usar `launch_persistent_context`.

### PW-013 — playwright/download
- **Sintoma:** `wait_for_event('download')` nunca resolve em popup/nova aba.
- **Causa-raiz:** evento é emitido pela Page que disparou; se download vai para outra aba, listener original não captura.
- **Solução:** `asyncio.create_task(page.wait_for_event('download'))` antes do click, ou listener no context.

### SE-019 — selenium/sessao
- **Sintoma:** precisa conectar Selenium a Chrome já aberto em debug.
- **Causa-raiz:** `webdriver.Chrome()` abre nova instância.
- **Solução:** `options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')`.

### PJE-002 — playwright/sessao
- **Sintoma:** sessão PJe expira em 30 min, script parcial falha na metade.
- **Causa-raiz:** timeout server-side fixo do PJe.
- **Solução:** renovar sessão a cada 20 min com click em ping/menu; dividir batch em chunks.

### PJE-003 — playwright/download
- **Sintoma:** "Download autos do processo" abre PDF embed em vez de baixar.
- **Causa-raiz:** Chrome PDF viewer intercepta.
- **Solução:** configurar `plugins.always_open_pdf_externally=true` nas prefs do contexto ou interceptar response.

### PJE-004 — playwright/selector
- **Sintoma:** "Incluir expediente=Sim" não seleciona via `select_option`.
- **Causa-raiz:** PrimeFaces (ver PW-009).
- **Solução:** mesma — `evaluate` + dispatch `change`.

### PJE-005 — playwright/iframe (tjmg-push)
- **Sintoma:** tabela de processos não encontrada em `page.locator`.
- **Causa-raiz:** URL `?iframe=true` renderiza tudo dentro de frame.
- **Solução:** `page.frame_locator('iframe').locator('table')`.

### PJE-008 — playwright/timeout
- **Sintoma:** PJe "tela branca" — body vazio após load.
- **Causa-raiz:** RichFaces faz push AJAX assíncrono; load dispara antes do conteúdo chegar.
- **Solução:** `wait_until='domcontentloaded'` + `wait_for_selector('#principal', state='attached', timeout=60_000)`.

### PJE-023 — requests/sessao
- **Sintoma:** baixar PDF PJe com `requests` após login via Playwright → 302 para `login.seam`.
- **Causa-raiz:** cookies de Playwright não foram transferidos.
- **Solução:** extrair cookies de `context.cookies()` e passar para `httpx.AsyncClient(cookies=...)`.

## Consulta por query

```bash
# Por tecnologia
jq '.[] | select(.tecnologia=="playwright")' ./python-base/03-FALHAS-SOLUCOES/db/falhas.json

# Por severidade
jq '.[] | select(.severidade=="bloqueador") | {id, sintoma}' ./python-base/03-FALHAS-SOLUCOES/db/falhas.json

# Por tag PJe
jq '.[] | select(.tags | index("pje"))' ./python-base/03-FALHAS-SOLUCOES/db/falhas.json
```

Base completa em `./python-base/03-FALHAS-SOLUCOES/db/falhas.json`.
