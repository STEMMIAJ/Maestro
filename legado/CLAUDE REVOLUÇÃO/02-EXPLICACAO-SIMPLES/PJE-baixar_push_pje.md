# PJE — baixar_push_pje.py (raciocínio do começo ao fim)

## O que é
Script Python que baixa todos os processos do PJe Push (sua aba de intimações) usando o navegador Chrome controlado por Selenium.

## Para que serve
Você não precisa abrir um por um, clicar, esperar, salvar. O script faz isso por você. Resultado: pasta com 1 PDF por processo.

## Onde fica
- Original: `~/stemmia-forense/src/pje/baixar_push_pje.py` (49KB)
- Atalho: `~/Desktop/STEMMIA Dexter/scripts/pje/` (link simbólico)

## Pré-requisitos (sem isso não roda)
1. Windows rodando no Parallels (PJe não funciona no Chrome do Mac)
2. Chrome em modo debug aberto na porta **9223**
   - Comando para abrir: `chrome.exe --remote-debugging-port=9223 --user-data-dir=C:\\chrome-pje`
3. Você já fez login no PJe com certificado VidaaS dentro desse Chrome
4. A aba do PJe Push está aberta

## Como rodar
```bash
cd ~/stemmia-forense/src/pje/
python3 baixar_push_pje.py
```

---

## Raciocínio passo a passo (como o script pensa)

### Passo 1 — Conectar ao Chrome existente
Em vez de abrir Chrome novo (perderia o login), o script conecta no Chrome que já está aberto na porta 9223.
```python
from selenium.webdriver.chrome.options import Options
opts = Options()
opts.debugger_address = "127.0.0.1:9223"
driver = webdriver.Chrome(options=opts)
```
**Por que assim:** o login PJe é por certificado digital (VidaaS), que só funciona no Windows. Conectar no Chrome já logado evita refazer login a cada execução.

### Passo 2 — Achar a aba do PJe Push
Procura entre as abas abertas qual tem `pje.tjmg.jus.br` no URL.
```python
for handle in driver.window_handles:
    driver.switch_to.window(handle)
    if "pje" in driver.current_url:
        break
```
**Por que:** você pode ter várias abas (Gmail, Calendar, etc). O script encontra a certa sozinho.

### Passo 3 — Listar processos da página
Encontra todos os links que levam a processos (cada linha da tabela de Push).
```python
processos = driver.find_elements(By.CSS_SELECTOR, "a[href*='ConsultaProcesso']")
```
**Resultado:** lista com 30, 50, 100 processos (depende do dia).

### Passo 4 — Para cada processo, abrir, baixar, salvar
Loop principal:
```python
for processo in processos:
    cnj = extrair_cnj(processo.text)   # ex: 5012345-67.2025.8.13.0024
    processo.click()                     # abre o processo
    sleep(3)                             # espera carregar
    botao_pdf = driver.find_element(By.ID, "btnDownloadPDF")
    botao_pdf.click()                    # baixa PDF
    aguardar_download(cnj)              # espera o arquivo aparecer
    mover_para_pasta(cnj)               # move pra pasta certa
    driver.back()                        # volta pra lista
```

### Passo 5 — Onde salva
Pasta de destino: `~/Desktop/Processos PJe/[ANO]/[CNJ].pdf`

Se já existe processo com mesmo CNJ, sobrescreve (versão mais nova).

### Passo 6 — Log de erros
Cada processo que falhar (timeout, link quebrado, certificado expirado) é gravado em:
`~/stemmia-forense/logs/pje_erros_[DATA].log`

Memória `project_pje_erros_log.md` no `~/.claude/projects/-Users-jesus/memory/` consolida.

---

## Exemplo concreto (rodada de 13/abr/2026)
- **Encontrados:** 47 processos
- **Baixados:** 44
- **Falharam:** 3 (todos por timeout do PJe — repetir depois)
- **Tempo total:** 18 minutos
- **Local:** `~/Desktop/Processos PJe/2025/` (44 PDFs novos)

---

## Problemas conhecidos

| Erro | Causa | Solução |
|------|-------|---------|
| `WebDriverException: cannot connect to chrome at 127.0.0.1:9223` | Chrome debug não está aberto | Abrir Chrome com `--remote-debugging-port=9223` no Windows |
| `TimeoutException` em vários processos | PJe lento ou caiu | Esperar 1h, rodar de novo |
| `NoSuchElementException: btnDownloadPDF` | PJe mudou layout | Inspecionar página nova, atualizar seletor |
| Certificado expirado | VidaaS venceu | Renovar VidaaS no portal |
| Download fica em "0 bytes" | Bloqueio antivírus | Adicionar pasta de download em exceção |

---

## Dependências
- Python 3.9+
- Selenium 4.x
- ChromeDriver (já bundled com Chrome moderno)
- Não precisa instalar nada com pip se usar `~/stemmia-forense/.venv/`

---

## O que NÃO faz (e você precisa fazer manual)
1. Não classifica os processos baixados (use o pipeline `/aceite-novo` depois)
2. Não gera petição de aceite (idem)
3. Não cadastra no Comunica PJe (pendente)
4. Não envia para Telegram (Bot existe mas falta integração)

---

## Histórico
- 13/abr/2026: funcionou pela primeira vez (44/47 processos)
- Última execução bem-sucedida: 13/abr/2026
- Sem rodar desde então (você ficou sem energia depois do incidente do pai)
