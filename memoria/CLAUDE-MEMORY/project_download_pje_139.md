---
name: Download PJe 139 processos — Fluxo completo que funciona
description: Fluxo TESTADO e FUNCIONANDO para baixar 139 processos PJe TJMG via Selenium. Inclui pré-requisitos, configuração, script, execução e troubleshooting detalhado.
type: project
originSessionId: 98656b59-fc0f-45d9-8f00-858ac201e9a9
---
# Download PJe TJMG — Fluxo Completo (FUNCIONA)

**Última atualização**: 2026-04-13
**Status**: FUNCIONANDO — script conectou ao Chrome existente, já logado, 55 linhas na tabela PUSH, downloads em andamento.

---

## 1. AMBIENTE

- **Onde roda**: Windows 11 ARM64 dentro de Parallels Desktop (Apple Silicon Mac)
- **PJe**: https://pje.tjmg.jus.br (TJMG, 1º Grau, Perito Jesus Penna)
- **Python**: `py` (Python 3 do Windows, ARM64)
- **Selenium**: `pip install selenium` (selenium-manager baixa ChromeDriver automaticamente)
- **Chrome**: Google Chrome para Windows (ARM64) com perfil isolado
- **Script Mac**: `~/stemmia-forense/src/pje/baixar_push_pje.py`
- **Script Windows (UNC)**: `\\Mac\Home\stemmia-forense\src\pje\baixar_push_pje.py`

**Why:** PJe só funciona no Windows com certificado digital VidaaS. Mac Chrome NÃO faz login no PJe.
**How to apply:** NUNCA tentar rodar no Mac. SEMPRE Parallels → Windows → CMD.

---

## 2. PRÉ-REQUISITOS (uma vez só)

### 2.1 Chrome com porta debug (9223)

O Chrome precisa rodar com `--remote-debugging-port=9223` para o Selenium conectar à sessão existente (com login VidaaS já feito).

**Opção A — abrir_pje_debug.bat:**
```
\\Mac\Home\Desktop\Projetos - Plan Mode\processos-pje\abrir_pje_debug.bat
```

**Opção B — iniciar_chrome_debug.bat:**
```
\\Mac\Home\stemmia-forense\src\pje\iniciar_chrome_debug.bat
```
(MATA Chrome existente antes de abrir novo)

**Opção C — Manual no CMD:**
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9223 --remote-allow-origins=* --user-data-dir="%LocalAppData%\Google\Chrome\User Data" --profile-directory=Default --start-maximized "https://pje.tjmg.jus.br/pje/login.seam"
```

### 2.2 Login manual VidaaS

1. Chrome abre na página de login do PJe
2. Clicar "Entrar com gov.br" ou VidaaS
3. Autenticar com certificado digital (ICP-Brasil)
4. Esperar chegar no Painel do Advogado
5. CONFIRMAR que aparece "Painel do Advogado" no título da aba

### 2.3 Selenium instalado

```cmd
py -m pip install selenium
```

---

## 3. SCRIPT — baixar_push_pje.py (v2 isolado, 864 linhas)

### 3.1 Constantes críticas

```python
PJE_BASE = "https://pje.tjmg.jus.br"
AUTOMATION_PROFILE = Path(r"C:\Users\jesus\Desktop\chrome-pje-profile")  # perfil isolado persistente
DEFAULT_DOWNLOAD_DIR = HOME / "Desktop" / "processos-pje"
WAIT_LOGIN = 300      # 5 min para login manual
WAIT_DOWNLOAD = 180   # 3 min para download de PDF
TIMEOUT_PROCESSO = 300 # 5 min por processo (ERA 90, MUDOU PARA 300 em 13/abr/2026)
```

**IMPORTANTE**: `TIMEOUT_PROCESSO` era 90s e causava timeout em PDFs grandes (>20MB). Mudou para 300s e resolveu.

### 3.2 Dois modos de conexão (criar_browser, linha 99)

**Modo 1 — Conectar ao Chrome existente (PREFERIDO, linhas 105-121):**
- Testa portas 9222 e 9223 com HTTP GET em `http://127.0.0.1:{porta}/json/version`
- Se responder com "Browser", cria ChromeDriver com `debuggerAddress: 127.0.0.1:{porta}`
- VANTAGEM: usa sessão já logada, não precisa re-autenticar
- FUNCIONA quando Chrome foi aberto com `--remote-debugging-port=9223`

**Modo 2 — Abrir Chrome novo (FALLBACK, linhas 123-156):**
- Usa perfil isolado em `C:\Users\jesus\Desktop\chrome-pje-profile`
- Flags: `--remote-debugging-port=9223`, `--disable-blink-features=AutomationControlled`, `detach=True`
- Chrome sobrevive após script terminar (detach=True)
- Limpa locks órfãos antes de abrir (SingletonLock, SingletonSocket, SingletonCookie)
- Se sessão expirou: `esperar_login()` espera 5 min para login manual VidaaS

### 3.3 Fluxo de download por processo (baixar_processo, linha 398)

```
Passo 1:  Verifica se PDF já existe no disco → pula se sim
Passo 2:  Salva handle da aba PUSH (aba_push = driver.current_window_handle)
Passo 3:  Encontra linha na tabela PUSH pelo número CNJ (busca texto + innerHTML)
Passo 4:  Encontra botão "Autos Digitais" na linha:
          - Por title: "auto", "digital", "visualizar", "abrir"
          - Por href: "autos", "processo", "visualiz"
          - Fallback: primeiro link não-destrutivo da linha
Passo 5:  Salva lista de abas abertas (abas_antes)
Passo 6:  Clica Autos Digitais via js_click (scrollIntoView + click via JavaScript)
Passo 7:  Espera 2s, aceita alert se houver, espera mais 2s
Passo 8:  Verifica se abriu nova aba:
          - Se sim: switch para nova aba
          - Se não: continua na mesma aba (AMBOS funcionam — NÃO forçar comportamento)
Passo 9:  Encontra ícone "Download autos do processo":
          - Por title: "download autos" (case-insensitive)
          - Por class: ".fa-download" ou "[class*='download']"
Passo 10: Clica ícone download via js_click
Passo 11: Espera iframe aparecer (até 15s, busca agressiva):
          - Loop: busca <iframe>, switch_to.frame(), verifica se tem elementos úteis
          - Se iframe vazio, volta para default_content e tenta próximo
Passo 12: Dentro do iframe: configura dropdowns (Select):
          - Encontra todos <select>, se valor = "Não" → muda para "Sim"
          - Isso inclui expediente/movimentos
Passo 13: Encontra botão DOWNLOAD final (_encontrar_botao_download_final):
          - Estratégia 1: Texto exato em buttons/links: "DOWNLOAD", "BAIXAR", "GERAR PDF", "GERAR", "OK"
          - Estratégia 2: Title parcial: [title*='ownload'], [title*='aixar'], [title*='erar']
          - Estratégia 3: XPath com translate: //button[contains(translate(...), 'DOWNLOAD')]
          - Estratégia 4: Classes PJe/RichFaces: .btn-primary, .btn-info, .rf-bt, .rich-btn
          - Estratégia 5: Qualquer input[type=submit] visível
          - Se não achou no iframe, tenta fora dele (switch_to.default_content)
Passo 14: Salva lista de arquivos na pasta de download (arquivos_antes)
Passo 15: Clica botão DOWNLOAD via js_click
Passo 16: Espera nova aba PDF ou download direto no disco:
          - Loop com timeout (TIMEOUT_PROCESSO):
            - Verifica novas abas (set(window_handles) - abas_antes_dl)
            - Verifica novos arquivos no disco (sem .crdownload)
Passo 17: Se abriu aba PDF: switch para ela, tenta Ctrl+S para salvar
Passo 18: Aguarda arquivo novo aparecer na pasta:
          - Loop: verifica listdir(), ignora .crdownload e .tmp
          - Timeout: restante do TIMEOUT_PROCESSO (max 300s total)
Passo 19: Renomeia arquivo para {CNJ_sanitizado}.pdf
Passo 20: Fecha abas extras (fechar_abas_extras):
          - Loop em window_handles, fecha tudo exceto aba_push
          - Switch de volta para aba_push
          - Agora está de volta na tabela PUSH, pronto para próximo processo
```

### 3.4 Paginação

- `proxima_pagina()`: clica em ">" ou "»" se não estiver disabled
- `ir_pagina(alvo)`: navega diretamente para página N (para retomar)
- Loop principal: extrai processos → baixa todos → proxima_pagina → repete

### 3.5 Proteções automáticas

- **Sessão expirada**: verifica antes de cada processo via `sessao_ativa()`, re-loga automaticamente
- **5 erros consecutivos**: verifica sessão e tenta re-logar
- **Tabela vazia**: verifica se é sessão expirada ou fim dos processos
- **Timeout hard por processo**: 300s — marca como "timeout" e pula para o próximo
- **Relatório JSON**: salvo ao final E em caso de erro, com log completo de cada operação

---

## 4. COMO EXECUTAR (passo a passo no CMD do Windows)

### 4.1 Verificar se Chrome já tem debug ativo

```cmd
netstat -an | findstr ":9223" | findstr "LISTENING"
```
Se NÃO mostra nada, abrir Chrome com debug (ver seção 2.1).

### 4.2 Teste com 1 processo

```cmd
pushd "\\Mac\Home\stemmia-forense\src\pje" && py baixar_push_pje.py --download-dir "%USERPROFILE%\Desktop\processos-pje" --limite 1
```

### 4.3 Lote completo (todos os processos)

```cmd
pushd "\\Mac\Home\stemmia-forense\src\pje" && py baixar_push_pje.py --download-dir "%USERPROFILE%\Desktop\processos-pje"
```

### 4.4 Retomar de página específica

```cmd
pushd "\\Mac\Home\stemmia-forense\src\pje" && py baixar_push_pje.py --download-dir "%USERPROFILE%\Desktop\processos-pje" --pagina 3
```

### 4.5 Matar processo antigo + rodar novo

```cmd
taskkill /f /im python.exe 2>nul & pushd "\\Mac\Home\stemmia-forense\src\pje" && py baixar_push_pje.py --download-dir "%USERPROFILE%\Desktop\processos-pje"
```

### 4.6 Via Claude Code (controle remoto do Mac)

1. `open_application("Parallels Desktop")` — traz VM para frente
2. `write_clipboard(comando)` — escreve comando no clipboard do Mac (sincroniza com Windows via Parallels)
3. Clicar dentro do CMD no Windows
4. Ctrl+C para limpar prompt
5. Right-click para colar
6. Enter para executar

**IMPORTANTE**: `write_clipboard` falha se Terminal do Mac estiver em primeiro plano (tier "click"). Sempre trazer Parallels para frente antes.

---

## 5. SAÍDA

- **PDFs**: `C:\Users\jesus\Desktop\processos-pje\{CNJ_sanitizado}.pdf`
- **Relatório**: `C:\Users\jesus\Desktop\processos-pje\relatorio-{data}-{hora}.json`
- **Chrome**: permanece aberto após script terminar (detach=True)

---

## 6. TROUBLESHOOTING DETALHADO

### Porta 9223 não responde
- Chrome não foi aberto com `--remote-debugging-port=9223`
- No ARM64/Parallels, a flag PODE ser ignorada se Chrome já rodava antes
- Solução: o script cai no Modo 2 (ChromeDriver direto com perfil isolado) e funciona
- Para forçar Modo 1: matar Chrome → reabrir com flag → confirmar porta com curl

### "Icone download nao encontrado"
- Script está na aba errada (não voltou para PUSH)
- Autos Digitais abriu na MESMA aba em vez de nova aba
- **NUNCA** usar `window.open()` ou `target='_blank'` — PJe usa onclick handlers JS, não URLs reais
- **NUNCA** modificar o click do Autos Digitais — deixar o js_click nativo

### Timeout em processos (antigo TIMEOUT=90)
- PDFs grandes (>20MB) levam mais de 90s para gerar no servidor do PJe
- Processo [5] da sessão de 13/abr: download com .crdownload ativo por >90s
- Solução: `TIMEOUT_PROCESSO = 300` (5 min) — tempo suficiente para qualquer PDF

### "CNJ nao encontrado na tabela"
- Tabela foi recarregada (sessão expirou → voltou para login)
- Script detecta e tenta re-logar automaticamente

### Lock do perfil ("SingletonLock")
- Chrome anterior crashou e deixou lock
- Script limpa automaticamente em `limpar_locks()` antes de abrir Chrome novo

### Comando pushd falha
- Path UNC `\\Mac\Home\...` precisa de `pushd` (não `cd /d`)
- `pushd` mapeia drive letter automaticamente (ex: V:, W:)

### SyntaxWarning: "\p" is invalid escape sequence
- Warning inofensivo no Python (linha 9 do script, string com \p)
- NÃO afeta execução. Para resolver: usar raw string `r"\p"` ou `\\p`

---

## 7. O QUE NUNCA FAZER

1. **NUNCA** matar o Chrome do usuário para liberar perfil padrão
2. **NUNCA** usar perfil padrão do Chrome — conflita com Chrome aberto do usuário
3. **NUNCA** modificar o click de Autos Digitais (window.open, target=_blank, etc.)
4. **NUNCA** fechar Chrome quando script termina — detach=True é obrigatório
5. **NUNCA** rodar no Mac — PJe requer Windows + certificado digital VidaaS
6. **NUNCA** mudar mais que o necessário — se funciona, só ajustar o parâmetro específico
7. **NUNCA** substituir js_click por click nativo — js_click evita ElementClickInterceptedException

---

## 8. HISTÓRICO DE PROBLEMAS E SOLUÇÕES

| Data | Problema | Causa raiz | Solução |
|------|----------|------------|---------|
| Mar/2026 | greenlet/ARM64 crash | greenlet DLL incompatível com ARM64 | Reescrever com Selenium puro (não usa greenlet) |
| Mar/2026 | connect_over_cdp falha | Porta 9222 não funciona cross-VM | Usar debuggerAddress local no Windows |
| Mar/2026 | \\Mac\Home inacessível | Caminho UNC precisa pushd | Usar `pushd "\\Mac\Home\..."` |
| Abr/2026 | Porta 9223 não ativa | Flag ignorada no ARM64/Parallels | Modo 2 (ChromeDriver direto) funciona |
| 13/abr/2026 | Timeout 90s muito curto | PDFs grandes levam >90s para gerar | TIMEOUT_PROCESSO = 300 |
| 13/abr/2026 | "Icone download nao encontrado" | Claude mudou click Autos para window.open, quebrou | REVERTIDO — NUNCA mexer no js_click nativo |

---

## 9. LIÇÃO PRINCIPAL

O fluxo nativo do PJe é:
1. Click no link "Autos Digitais" → PJe decide se abre nova aba ou carrega na mesma
2. Na página de autos, click no ícone de download → abre iframe com configuração
3. No iframe, click em DOWNLOAD → PJe gera PDF e inicia download

**Cada etapa usa onclick handlers JavaScript internos do PJe.** Tentar "melhorar" qualquer click (forçar nova aba, trocar href, adicionar target) QUEBRA o fluxo porque o JavaScript do PJe não é executado.

A única mudança segura é ajustar timeouts e configurações de espera. O fluxo de clicks deve permanecer intocado.
