---
titulo: Download de documentos PJe via Playwright conectando a Chrome debug remoto (portas 9223/9222)
tipo: evidencia
dominio: Python
subtopico: Playwright / Selenium + CDP
nivel_demonstrado: 3
versao: 0.1
status: validada
ultima_atualizacao: 2026-04-23
fonte: /Users/jesus/Desktop/STEMMIA Dexter/src/pje/emergencia/baixar_documentos_processo_aberto.py
---

## Descrição
Script async que conecta via Chrome DevTools Protocol (CDP) a uma instância Chrome ja aberta
no Windows/Parallels (portas 9223 e 9222), injeta JS no DOM do PJe para descobrir links de documento
com heurística (regex de docId 6–12 dígitos + visibilidade + filtros negativos tipo "fixar/pin/copiar"),
aciona clique programático e aguarda download. Evita login automático, opera sobre sessão humana.

## Arquivo real
`/Users/jesus/Desktop/STEMMIA Dexter/src/pje/emergencia/baixar_documentos_processo_aberto.py`

## Habilidade demonstrada
- `Python.Playwright / Selenium` — 3 (CDP, JS injection, async handlers)
- `Python.async/await` — 2 (asyncio + playwright.async_api)
- `APIs.consumir REST` — 2 (CDP endpoint /json/version)
- `Automação doc.` — 3 (PDF do PJe baixado sem clique humano)

## Trecho relevante
```python
DEFAULT_HOSTS = "127.0.0.1,10.211.55.3"
DEFAULT_PORTS = "9223,9222"
CNJ_RE = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")
DOC_ID_RE = re.compile(r"\b\d{6,12}\b")
MIN_BYTES = 900

try:
    from playwright.async_api import Error as PlaywrightError, async_playwright
except ImportError:
    print("Playwright nao instalado. Rode: python -m pip install playwright")
    sys.exit(1)
```

Heurística JS injetada para achar botão de download:
```javascript
const positive = /(download|baixar|visualizar|abrir|documento|pje-bin|
  processodocumento|iddocumento|pdf|file-pdf|fa-file|glyphicon-file)/.test(blob);
if (!includeAll && !positive && !isTextLink) continue;
el.scrollIntoView({ block: "center", inline: "center" });
el.click();
```

## Data
2026-04 (pasta `emergencia/` ativa em Mutirão 125). Sem git log — arquivo não versionado ainda.

## Validação externa
**Média** — rodou em produção durante o Mutirão de downloads (referência em `project_download_pje_139.md`, fluxo funcionando desde 13/abr/2026). Zero computer-use, só CDP.

## Limitações conhecidas
- Quebra se PJe mudar DOM dos ícones de download (regex positiva depende de classes atuais).
- Depende de perfil Chrome do Parallels estar aberto na página certa — sem auto-login.
- Sem retry com backoff formal; só `suppress` + timeout 30s.
