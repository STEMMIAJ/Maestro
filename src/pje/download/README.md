# baixar_push_pje.py — Download em massa dos processos do PUSH

## O que esse fluxo faz (1 frase)
Abre o PJe, espera o Dr. Jesus logar uma vez, percorre TODAS as páginas da aba PUSH, baixa o PDF de "autos completos" de cada processo, verifica se o conteúdo bate com o CNJ (detecta bug de cache do PJe) e salva com nome padronizado — com dedup persistente entre execuções.

## Arquivos da pasta
```
download/
├── baixar_push_pje.py    (1344 linhas — orquestrador principal)
├── pje_verificacao.py    (módulo auxiliar: verifica conteúdo do PDF, Telegram, janela TJMG)
└── _analise-erros/       (pasta pra investigações futuras)
```

---

## Bloco 1 — Configuração: URLs, perfil do Chrome, timeouts (linhas 48-76)
```python
PJE_BASE = "https://pje.tjmg.jus.br"
PJE_LOGIN = f"{PJE_BASE}/pje/login.seam"
PJE_PAINEL = f"{PJE_BASE}/pje/Painel/painel_usuario/advogado.seam"
DEFAULT_DOWNLOAD_DIR = HOME / "Desktop" / "processos-novos"
ORDEM_COMARCA_DEFAULT = ["0680", "0627", "0105", "0396"]  # Taiobeiras→GV→Mantena
SLEEP_ENTRE_PROCESSOS = 20
PAUSA_LONGA_A_CADA = 10
AUTOMATION_PROFILE = HOME / "Desktop" / "chrome-pje-profile"
WAIT_LOGIN = 300     # 5 min
TIMEOUT_PROCESSO = 300  # 5 min por processo
```
**Explicação:** onde é o PJe, onde salvar PDFs, qual perfil de Chrome usar (fixo, persistente), quantos segundos esperar em cada etapa, e a ordem de prioridade de comarcas (os últimos 4 dígitos do CNJ identificam a comarca).
**Analogia:** lista de endereços de plantão + lista de prioridades do pronto-socorro. Taiobeiras e Rio Pardo primeiro (pacientes mais críticos), Mantena por último.
**Por que importa:** mudar `ORDEM_COMARCA_DEFAULT` muda QUEM é atendido primeiro quando a sessão do PJe pode cair a qualquer minuto.

---

## Bloco 2 — Índice de dedup persistente (fix do loop infinito) (linhas 78-135)
```python
_DEDUP_INDEX = {}   # {cnj: {"path": str, "kb": int, "ts": str, "comarca": str}}
_CNJS_BAIXADOS_SESSAO = set()

def _carregar_dedup_index(download_dir):
    _DEDUP_INDEX_PATH = Path(download_dir) / "_downloads_feitos.json"
    if _DEDUP_INDEX_PATH.exists():
        _DEDUP_INDEX = json.loads(_DEDUP_INDEX_PATH.read_text(encoding="utf-8"))

def _marcar_baixado(cnj, destino_path, kb, comarca=""):
    _DEDUP_INDEX[cnj] = {"path": ..., "kb": ..., "ts": ..., "comarca": comarca}
    _salvar_dedup_index()

def _ja_baixado_idx(cnj):
    entry = _DEDUP_INDEX.get(cnj)
    if entry and Path(entry["path"]).exists():
        return entry
    return None
```
**Explicação:** mantém um arquivo `_downloads_feitos.json` que mapeia CNJ → caminho real do PDF. Consultado ANTES de tentar baixar.
**Analogia:** livro de protocolo na portaria — antes de ligar pro paciente pra confirmar consulta, você confere se ele já foi atendido hoje.
**Por que importa:** FIX 19/abr/2026 — o PJe salva PDFs com nome hash (sem CNJ), então a busca por "CNJ no nome do arquivo" falhava e o script baixava o MESMO processo 7x em loop. Esse índice resolve.

---

## Bloco 3 — Log estruturado (linhas 138-161)
```python
_log_entries = []
def log(msg, level="INFO", selector=None, elapsed=None, arquivo=None, erro=None):
    entry = {"timestamp": ..., "level": level, "msg": msg}
    if selector: entry["selector"] = selector
    if elapsed is not None: entry["elapsed_s"] = round(elapsed, 2)
    ...
    _log_entries.append(entry)
```
**Explicação:** cada linha de log vira um dict JSON com timestamp, nível, mensagem, seletor CSS usado, tempo decorrido, caminho do arquivo, erro. Tudo acumulado em `_log_entries` e serializado no relatório final.
**Analogia:** prontuário estruturado — não escreve "paciente passou mal", escreve "12:03 | PAM 70/40 | bradicardia 42 | responsivo".
**Por que importa:** quando algo dá errado, o relatório JSON permite reconstruir exatamente qual seletor travou, quanto tempo cada etapa demorou — debugar sem precisar reproduzir.

---

## Bloco 4 — Criar ou conectar ao Chrome (linhas 164-235)
```python
def criar_browser(download_dir):
    # MODO 1: Tenta conectar no Chrome já rodando (portas 9222, 9223)
    for porta in [9222, 9223]:
        resp = urllib.request.urlopen(f"http://127.0.0.1:{porta}/json/version", timeout=3)
        if "Browser" in data:
            opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{porta}")
            driver = webdriver.Chrome(options=opts)
            return driver

    # MODO 2: Abre Chrome novo com perfil isolado
    opts.add_argument(f"--user-data-dir={AUTOMATION_PROFILE}")
    opts.add_argument("--remote-debugging-port=9223")
    prefs = {
        "download.default_directory": str(download_dir),
        "plugins.always_open_pdf_externally": True,
    }
```
**Explicação:** primeiro tenta achar um Chrome já aberto em modo debug. Se não achar, abre um Chrome próprio com perfil fixo (`~/Desktop/chrome-pje-profile`) e configura ele pra salvar PDFs direto na pasta (sem abrir o visualizador).
**Analogia:** chega na clínica — se o consultório já tá aberto com luz acesa, entra. Se não, destranca e configura (computador, impressora, prontuário).
**Por que importa:** perfil fixo = cookies/sessão sobrevivem entre execuções. Não precisa logar toda vez. E `always_open_pdf_externally=True` = PDF baixa direto, não abre viewer.

---

## Bloco 5 — Login manual + detecção automática (linhas 238-284)
```python
def esperar_login(driver):
    WebDriverWait(driver, WAIT_LOGIN).until(
        lambda d: any([
            "painel_usuario" in d.current_url,
            "Painel" in d.title,
            "Jesus Penna" in d.page_source,
            "Quadro de avisos" in d.page_source,
        ])
    )

def sessao_ativa(driver):
    if "login" in url or "auth" in url:
        return False
    if "CPF/CNPJ" in src and "Senha" in src:
        return False
    return True

def relogar(driver):
    driver.get(PJE_LOGIN)
    return esperar_login(driver)
```
**Explicação:** três funções relacionadas — esperar login inicial (5min max, detecta por 4 sinais diferentes), checar se ainda está logado, fazer re-login quando detectar que caiu.
**Analogia:** fica de olho na porta — sabe se a porta está aberta (sessão ativa), esperando abrirem (esperar_login), ou se precisa bater de novo (relogar).
**Por que importa:** sessão do PJe cai a cada 30-60 min. Sem re-login automático, o script quebra no meio de 300 processos.

---

## Bloco 6 — Navegação até a aba PUSH (linhas 289-336)
```python
def navegar_para_push(driver):
    driver.get(PJE_PAINEL)
    seletores = [
        (By.LINK_TEXT, "PUSH"),
        (By.PARTIAL_LINK_TEXT, "PUSH"),
        (By.XPATH, "//a[normalize-space(text())='PUSH']"),
        (By.CSS_SELECTOR, "a[href*='Push'], a[href*='push']"),
    ]
    for by, sel in seletores:
        els = driver.find_elements(by, sel)
        for el in els:
            driver.execute_script("arguments[0].click();", el)
            return True
    # Fallback: URL direta
    driver.get(f"{PJE_BASE}/pje/Push/listView.seam?iframe=true")
```
**Explicação:** vai pro painel, procura link "PUSH" de 4 jeitos diferentes, clica. Se nada funciona, usa URL direta.
**Analogia:** entrar no hospital e procurar a UTI — pode ter placa escrita "UTI", "U.T.I.", "Terapia Intensiva", ou você pega o elevador direto pro 3º andar.
**Por que importa:** PJe muda texto/estrutura. Múltiplos seletores = sobrevive a mudanças pequenas.

---

## Bloco 7 — Extrair lista de CNJs da tabela atual (linhas 341-391)
```python
def extrair_processos(driver):
    for selector in ["table tbody tr", "table tr", ".rich-table-row", ".rf-dt-r", "tr"]:
        rows = driver.find_elements(By.CSS_SELECTOR, selector)
        if len(rows) > 2:
            break
    for i, row in enumerate(rows):
        for cell in cells:
            m = CNJ_RE.search(cell.text.strip())
            if m:
                num = m.group()
                break
        if num and num not in cnjs_vistos:
            processos.append({"index": i, "numero": num})
```
**Explicação:** acha a tabela de processos, percorre cada linha, extrai o primeiro CNJ que bate com o regex (formato `1234567-89.2024.8.13.0000`).
**Analogia:** ler a lista de pacientes do dia — olha linha por linha, extrai só o nome (CNJ), ignora o resto.
**Por que importa:** é a base pro loop — sem essa lista, o script não sabe o que baixar.

---

## Bloco 8 — Download de UM processo (o coração do fluxo) (linhas 477-813)
```python
def baixar_processo(driver, idx, num, download_dir):
    # 1. Dedup (3 camadas: sessão, índice JSON, conteúdo do PDF)
    if num in _CNJS_BAIXADOS_SESSAO: return "ja-baixado-sessao"
    if _ja_baixado_idx(num): return "ja-baixado-idx"
    if _encontrar_valido_existente(): return "ja-baixado"

    # 2. Encontrar linha na tabela, clicar "Autos Digitais"
    row = [r for r in rows if num in r.text][0]
    autos_btn = [link for link in row.find_elements(By.TAG_NAME, "a") if "auto" in link.get_attribute("title").lower()][0]
    js_click(driver, autos_btn)

    # 3. Trocar pra nova aba (ou mesma, se abriu ali)
    novas = set(driver.window_handles) - abas_antes
    if novas: driver.switch_to.window(novas.pop())

    # 4. Clicar ícone "Download autos do processo"
    dl_btn = [el for el in ... if "download autos" in el.get_attribute("title").lower()][0]
    js_click(driver, dl_btn)

    # 5. Entrar no iframe da página de download
    for iframe in iframes:
        driver.switch_to.frame(iframe)
        if driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit']"): break

    # 6. Configurar dropdowns "Incluir expediente/movimentos?" → Sim
    for sel in selects:
        if s.first_selected_option.text.strip() == "Não":
            s.select_by_visible_text("Sim")

    # 7. Clicar botão DOWNLOAD final, aguardar PDF (timeout 3min)
    dl_final, sel_info = _encontrar_botao_download_final(driver)
    js_click(driver, dl_final)
    novo_arquivo, tempo_dl = aguardar_download(download_dir, arquivos_antes, timeout=restante)

    # 8. VERIFICAR CONTEÚDO — bug do cache do PJe
    conferido, cnj_real, comarca, razao = verificar_conteudo(caminho, num)
    if not conferido:
        # Quarentena
        mover_para_quarentena(caminho, "_invalidos", novo_nome)
        return "conteudo-divergente"

    # 9. Renomear com padrão CNJ__comarca.pdf
    destino = download_dir / f"{safe}__{slug_comarca(comarca)}.pdf"
    caminho.rename(destino)
    _marcar_baixado(num, destino, sz // 1024, comarca=comarca)
    return "ok"
```
**Explicação:** 9 etapas sequenciais com timeout hard de 5min por processo. Detalhe crítico na etapa 8: o PJe tem bug de cache onde às vezes entrega o PDF do processo ANTERIOR — o script abre o PDF, lê o CNJ da primeira página e compara com o esperado.
**Analogia:** entregar medicação — confere nome no prontuário, confere nome no remédio, confere dose, registra. Se bater errado: segrega, não administra.
**Por que importa:** é o core do fluxo. A verificação de conteúdo (fix 17/abr) é o que impede que o Dexter acumule PDFs trocados — sem isso, Dr. Jesus laudaria o caso errado.

---

## Bloco 9 — Aguardar download real (sem .crdownload) (linhas 413-429)
```python
def aguardar_download(download_dir, arquivos_antes, timeout=WAIT_DOWNLOAD):
    while time.time() - t0 < timeout:
        time.sleep(3)
        agora = set(os.listdir(str(download_dir)))
        novos = agora - arquivos_antes
        completos = [f for f in novos if not f.endswith((".crdownload", ".tmp"))]
        if completos:
            return completos[0], time.time() - t0
```
**Explicação:** fica olhando a pasta de download — só retorna quando aparece arquivo novo SEM extensão `.crdownload` ou `.tmp` (que indicam download incompleto).
**Analogia:** esperar a impressora terminar — não pega o papel antes de parar de chiar.
**Por que importa:** PDF incompleto corrompe. Renomear antes da hora = PDF quebrado.

---

## Bloco 10 — Paginação (RichFaces é chato) (linhas 832-998)
```python
def detectar_total_paginas(driver):
    for sel in [".rf-ds-nmb", ".rf-ds span", "[class*='ds-nmb']"]:
        els = driver.find_elements(By.CSS_SELECTOR, sel)
        for el in els:
            if txt.isdigit() and 1 <= int(txt) <= 200:
                max_pag = max(max_pag, int(txt))

def proxima_pagina(driver, pag_atual=0):
    prox = pag_atual + 1
    # 1. span.rf-ds-nmb com texto = próxima
    # 2. span.rf-ds-btn-next (botão ›)
    # 3. Qualquer span/a com texto da próxima
    # 4. Símbolos › » >
    # 5. JavaScript puro (nuclear)
```
**Explicação:** o PJe usa RichFaces e renderiza paginação como `<span>` (não `<a>`). Cinco estratégias em cascata pra avançar página, da mais específica (classe RichFaces) à nuclear (JS puro varrendo o DOM).
**Analogia:** passar de sala em sala no corredor — se a porta 2 está trancada, tenta a porta dos fundos, tenta a janela, tenta escalar.
**Por que importa:** sem paginação funcionando, o script baixa só a primeira página (10-20 processos) e para. Dr. Jesus tem 300+ processos no PUSH.

---

## Bloco 11 — Janela TJMG (13h-19h PJe indisponível) + Telegram + Retry (linhas 1034-1079)
```python
if _VERIF_OK and not args.ignorar_janela:
    disp, msg_janela = janela_disponivel()
    if not disp:
        log(msg_janela, "WAIT")
        esperar_janela_liberar(log_fn=...)

if args.retry:
    relatorios = sorted(glob.glob(str(dl_dir / "relatorio-*.json")))
    ultimo = json.load(open(relatorios[-1]))
    retry_cnjs = [p["numero"] for p in ultimo["processos"] if p["status"] not in ("ok", "ja-baixado")]
```
**Explicação:** o PJe TJMG sai do ar entre 13h-19h para manutenção. Se rodar nesse período, o script PAUSA e espera abrir. Com `--retry`, ele lê o último relatório e processa só os que falharam.
**Analogia:** horário de visita do hospital — não adianta chegar às 15h, fica no estacionamento esperando liberar.
**Por que importa:** roda sem supervisão em horário de almoço/madrugada — não trava no cadeado do TJMG.

---

## Bloco 12 — Loop principal (página por página, com recuperação de sessão) (linhas 1093-1292)
```python
while True:
    procs = extrair_processos(driver)
    procs = ordenar_por_comarca(procs, ordem_comarca)
    for proc in procs:
        if 0 < args.limite <= total_ok: break
        if not sessao_ativa(driver):
            relogar(driver); navegar_para_push(driver); ir_pagina_direta(driver, pag); break
        if proc["numero"] in cnjs_processados: continue
        r = baixar_processo(driver, proc["index"], proc["numero"], dl_dir)
        if r["status"] in ("ok", "ja-baixado"):
            total_ok += 1
            if r.get("conferido"): total_ok_conferido += 1
            if total_ok_conferido % PAUSA_LONGA_A_CADA == 0: time.sleep(SLEEP_PAUSA_LONGA)
        time.sleep(max(1, args.sleep))
    avancou = proxima_pagina(driver, pag)
    if not avancou: break
    pag += 1
```
**Explicação:** para cada página, extrai lista, ordena por comarca prioritária, baixa um por um. Checa sessão antes de cada download. Pausa longa (3 min) a cada 10 OK conferidos pra não sobrecarregar o PJe. Notifica Telegram a cada 10 confirmados.
**Analogia:** ronda hospitalar — enfermeira passa leito a leito, checa sinais vitais, anota, pausa pra tomar café a cada andar, avisa a médica no WhatsApp no fim de cada ala.
**Por que importa:** é o "diretor" do fluxo. Aqui é onde acontece a resiliência: sessão cai? relogar. PJe travou? pausa longa. Página vazia? não assume fim, continua. 5 erros seguidos? força verificação de sessão.

---

## Bloco 13 — Relatório final JSON (linhas 1294-1324)
```python
report["fim"] = datetime.now().isoformat()
report["baixados"] = total_ok
report["conferidos"] = total_ok_conferido
report["invalidos"] = total_invalidos
report["erros"] = total_err
report["log"] = _log_entries
rpath = dl_dir / f"relatorio-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
with open(rpath, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
```
**Explicação:** salva um JSON com início/fim da execução, config usada, resultado de cada processo individual, e log estruturado completo.
**Analogia:** alta hospitalar — resumo de TUDO que aconteceu no plantão. Base pra auditoria e pra próxima execução (`--retry`).
**Por que importa:** sem esse JSON, não dá pra saber o que deu errado E não dá pra rodar `--retry`.

---

## Como rodar
```bash
# Baixar tudo (vai até acabar ou cair)
python baixar_push_pje.py

# Testar com 1 processo
python baixar_push_pje.py --limite 1

# Pasta customizada
python baixar_push_pje.py --download-dir "C:\pdfs"

# Começar na página 3
python baixar_push_pje.py --pagina 3

# Só refazer os que falharam no último relatório
python baixar_push_pje.py --retry

# Excluir uma comarca
python baixar_push_pje.py --excluir-comarca 0396

# Mudar ordem de prioridade
python baixar_push_pje.py --ordem-comarca 0627,0105,0680,0396

# Notificações no Telegram
python baixar_push_pje.py --telegram

# Ignorar janela de manutenção TJMG (não recomendado)
python baixar_push_pje.py --ignorar-janela

# Pausa maior entre processos
python baixar_push_pje.py --sleep 30
```

## Erros conhecidos
- **"Loop infinito baixando o mesmo CNJ 7x"** → CORRIGIDO em 19/abr/2026 via `_downloads_feitos.json`. Se voltar, checar se `_dedup_index_path` existe na pasta de download.
- **"PDF com conteúdo divergente" (quarentena em `_invalidos/`)** → bug do cache do PJe. O script detecta e segrega automaticamente. Abrir o PDF em `_invalidos/` e conferir o nome do arquivo (ele registra qual CNJ veio no lugar).
- **"Botão DOWNLOAD não encontrado"** → PJe mudou o iframe/botão final. Investigar com `driver.page_source` ou abrir manualmente no mesmo processo.
- **"5 erros consecutivos"** → script força checagem de sessão. Se sessão está ok, provavelmente PJe está fora do ar.
- **"Timeout 300s"** → processo muito grande (>100MB). Aumentar `TIMEOUT_PROCESSO` (linha 74).
- **"Tabela vazia mas ainda há páginas"** → sessão expirou silenciosa. Script tenta re-login automático.
- **Chrome não conecta na porta 9223** → rodar `limpar_locks()` manualmente ou apagar `~/Desktop/chrome-pje-profile/Singleton*`.

## Dependências
- `selenium` (`pip install selenium`)
- Chrome/Chromium instalado
- Módulo local `pje_verificacao.py` (mesma pasta — core do fix do cache)
- Python 3.9+

---

Gerado em 2026-04-19 | Revisar a cada mudança estrutural
