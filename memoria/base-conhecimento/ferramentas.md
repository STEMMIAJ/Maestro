# Ferramentas — Bugs, Workarounds e Preferências

## Modelos de IA

| Modelo | Status | Observação |
|--------|--------|------------|
| Claude Opus 4.6 | Padrão para tudo | NUNCA rebaixar sem autorização |
| Gemini 2.5-flash-lite | Preferido para tarefas rápidas | NÃO usar Gemini 2.0 (inferior) |
| Gemini 2.5 Pro | Para análises longas | Quando Claude não disponível |

## Claude Code

### Bugs Conhecidos
- `git status -uall` causa memory issues em repos grandes — NUNCA usar
- Hooks excessivos (28+) degradam performance — manter máximo 6 essenciais
- Agent Teams requer `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` — essencial, não desativar
- Compactação de contexto perde informações — salvar síntese ANTES de compactar

### Workarounds
- Subagentes sempre Opus: `CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-6`
- Se MCP falhar: reiniciar com `claude --mcp-restart`
- Se hook falhar: verificar permissões do script, não do hook config

## pdftotext

### Bug
- Retorna vazio em PDFs escaneados (imagens, não texto)
- PDFs do TRT frequentemente escaneados

### Workaround
```bash
texto=$(pdftotext arquivo.pdf -)
if [ ${#texto} -lt 50 ]; then
    tesseract arquivo.pdf saida --oem 1 --psm 6
fi
```

## reportlab / fpdf2

### Bug
- reportlab: API excessivamente verbosa para documentos jurídicos
- fpdf2: encoding quebrado para caracteres especiais (ç, ã, é)

### Workaround
- Usar geração via XML como intermediário para petições

## Selenium (download PJe)

### Configuração funcional
```python
options = webdriver.ChromeOptions()
options.debugger_address = "localhost:9223"
driver = webdriver.Chrome(options=options)
```
- Chrome precisa estar aberto com `--remote-debugging-port=9223`
- Perfil isolado em `~/.chrome-pje/`

### Bugs conhecidos
- Se Chrome fechar, Selenium perde conexão — reabrir Chrome antes
- Timeout padrão insuficiente para PJe — usar `WebDriverWait(driver, 30)`
- PJe usa iframes — sempre `driver.switch_to.frame()` antes de interagir

## N8N

### Servidor
- URL: https://n8n.srv19105.nvhm.cloud
- MCP funciona — NUNCA dizer que não pode acessar N8N
- Workflows ativos: análise pericial, pesquisador de produtos

### Bugs conhecidos
- Workflow de análise pericial funciona local mas trava no cloud (limite de execução)
- Importação de credenciais não transfere senhas — reconfigurar manualmente

## Tesseract OCR

### Configuração
```bash
tesseract input.pdf output --oem 1 --psm 6 -l por
```
- `--oem 1`: LSTM neural network (melhor qualidade)
- `--psm 6`: bloco de texto uniforme (melhor para documentos)
- `-l por`: idioma português

### Limitação
- PDFs com mais de 20 páginas: dividir antes com `pdfseparate`
- Qualidade depende da resolução do escaneamento (mínimo 200 DPI)

## FTP (deploy site)

- Servidor: Nuvem Fácil
- Senha atualizada em 16/mar/2026
- Sempre subir PDFs/HTMLs pro site via FTP + atualizar Planner
