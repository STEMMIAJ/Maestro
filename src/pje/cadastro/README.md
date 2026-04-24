# incluir_push.py — Cadastrar processos no PUSH do PJe TJMG

## O que esse fluxo faz (1 frase)
Lê uma lista de CNJs (números de processos), abre o PJe no navegador, espera o Dr. Jesus fazer login uma vez, e cadastra cada processo na aba PUSH — que é o "serviço de assinatura" do PJe que manda intimação quando o processo mexe.

---

## Bloco 1 — Configuração: onde está a lista, onde é o PJe (linhas 38-47)
```python
PJE_LOGIN = "https://pje.tjmg.jus.br/pje/login.seam"
PJE_PUSH = "https://pje.tjmg.jus.br/pje/Push/listView.seam"
USER_DATA = Path.home() / ".pje-browser-data"
LISTA_JSON = Path.home() / "Desktop/STEMMIA Dexter/LISTA-COMPLETA-PUSH.json"
LISTA_TXT = Path.home() / "Desktop/STEMMIA Dexter/AUTOMAÇÃO/lista-inclusao-push.txt"
```
**Explicação:** define os endereços do PJe (login e aba PUSH), o diretório onde o navegador vai guardar cookies/sessão, e os dois caminhos possíveis da lista de processos (JSON é prioridade; TXT é fallback).
**Analogia:** como anotar no caderno o endereço do cartório e onde está a lista de pacientes antes de sair de casa.
**Por que importa:** se o arquivo da lista mudar de lugar, o script não acha nada e para. Mexer aqui é o primeiro passo quando o fluxo "não vê os processos".

---

## Bloco 2 — Seletores candidatos: como achar o campo certo no HTML do PJe (linhas 50-78)
```python
SELETORES_CNJ = [
    "input[id*='numeroProcesso']",
    "input[id*='numProcesso']",
    ...
]
SELETORES_BTN = [
    "input[value='Incluir']",
    "button:has-text('Incluir')",
    ...
]
```
**Explicação:** listas de "endereços" possíveis dentro da página (seletores CSS). O script tenta cada um até achar um que funcione.
**Analogia:** como entrar numa clínica nova e procurar o balcão de triagem — você olha para placas "Recepção", "Atendimento", "Entrada". Se uma não existe, tenta a próxima.
**Por que importa:** o PJe muda o HTML entre versões. Ter várias opções = o script sobrevive a atualização sem precisar reescrever.

---

## Bloco 3 — Carregar a lista de processos (linhas 93-146)
```python
def carregar_lista(arquivo=None):
    if LISTA_JSON.exists():
        return _carregar_json(LISTA_JSON)
    if LISTA_TXT.exists():
        return _carregar_txt(LISTA_TXT)
```
**Explicação:** lê o arquivo JSON ou TXT, extrai os CNJs (o número no formato `1234567-89.2024.8.13.0000`), joga fora o que não encaixa nesse formato.
**Analogia:** como pegar a lista do dia: abre a agenda, risca os rabiscos ilegíveis, fica só com os nomes válidos.
**Por que importa:** garante que nenhum lixo (linha em branco, comentário, número mal digitado) vai tentar ser cadastrado no PJe.

---

## Bloco 4 — Abrir ou conectar ao navegador (linhas 153-201)
```python
async def conectar_cdp(porta=9222):
    cdp_url = f"http://127.0.0.1:{porta}"
    browser = await pw.chromium.connect_over_cdp(cdp_url)
    ...

async def abrir_browser_standalone():
    browser = await pw.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA),
        headless=False,
        ...
    )
```
**Explicação:** tenta primeiro conectar num Chrome já aberto em modo debug (porta 9222). Se não achar, abre um Chromium próprio com perfil persistente (cookies salvos entre execuções).
**Analogia:** como chegar no consultório e perguntar "a sala 3 já está aberta?" — se sim, entra. Se não, destranca e abre.
**Por que importa:** se já tem um Chrome aberto com você logado no gov.br, o script usa ele e pula o login. Se não, ele abre um próprio. Flexível.

---

## Bloco 5 — Login VidaaS / gov.br (manual, o script só espera) (linhas 208-235)
```python
async def aguardar_login(page):
    await page.goto(PJE_LOGIN, wait_until="domcontentloaded", timeout=60000)
    ...
    for i in range(300):  # 5 min max
        await page.wait_for_timeout(1000)
        url = page.url.lower()
        if "login" not in url and "sso" not in url and "gov.br" not in url:
            log("Login detectado!", "OK")
            return True
```
**Explicação:** abre a tela de login do PJe e fica verificando a cada segundo se a URL mudou — quando a URL não tem mais "login"/"sso"/"gov.br", é porque o usuário autenticou com certificado.
**Analogia:** porteiro do prédio que fica de olho na portaria — ele não abre a porta pra você; espera você mostrar o crachá no leitor, e só então libera o elevador.
**Por que importa:** o VidaaS exige o certificado digital do médico, que só ele pode inserir. O script não tenta automatizar isso — só aguarda. Timeout de 5 min.

---

## Bloco 6 — Navegar até a aba PUSH (linhas 242-284)
```python
async def navegar_push(page):
    for url in [PJE_PUSH, PJE_PUSH_ALT]:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        ...
        for sel in SELETORES_CNJ:
            el = page.locator(sel).first
            if await el.is_visible(timeout=2000):
                return True
```
**Explicação:** tenta duas URLs do PUSH, verifica se o campo de CNJ apareceu. Se não apareceu, clica em links tipo "Incluir"/"Novo"/"Adicionar".
**Analogia:** entrar no cartório e procurar o guichê certo — tenta a sala A, depois a B, e se não achar pergunta na recepção.
**Por que importa:** PJe às vezes muda URL ou muda o nome do botão. Ter fallback = não trava no primeiro obstáculo.

---

## Bloco 7 — Incluir UM processo no PUSH (linhas 307-368)
```python
async def incluir_processo(page, cnj, observacao, dry_run=False):
    campo_cnj = await encontrar_elemento(page, SELETORES_CNJ, "CNJ")
    await campo_cnj.fill(cnj)
    ...
    btn = await encontrar_elemento(page, SELETORES_BTN, "Incluir")
    await btn.click()
    ...
    if any(t in body_lower for t in ["já cadastrado", "já existe", "duplicado"]):
        return "duplicata"
    if any(t in body_lower for t in ["sucesso", "incluído", "adicionado"]):
        return "ok"
```
**Explicação:** preenche o CNJ, preenche a observação (se tiver campo), clica Incluir, e lê o texto da página depois pra detectar se foi sucesso, duplicata ou erro.
**Analogia:** preencher ficha de cadastro no balcão: escreve nome, observação, entrega. Depois lê a resposta do atendente ("já cadastrado" / "pronto" / "número inválido").
**Por que importa:** é o coração do script. Três saídas possíveis: `ok` (cadastrou), `duplicata` (já estava), `erro` (algum problema). Cada uma conta no relatório final.

---

## Bloco 8 — Screenshot em caso de erro (linhas 380-390)
```python
async def _screenshot_erro(page, cnj):
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    path = SCREENSHOTS_DIR / f"erro_push_{cnj_limpo}_{ts}.png"
    await page.screenshot(path=str(path))
```
**Explicação:** quando falha a inclusão de um processo, tira print da tela e salva numa pasta com o CNJ e data no nome.
**Analogia:** médico bate foto do RX quando vê algo estranho — pra mostrar depois pro especialista.
**Por que importa:** na hora de debugar "por que falhou?", o print mostra exatamente o que o PJe estava exibindo. Sem isso, é adivinhar.

---

## Bloco 9 — Modo `--descobrir` (investigação) (linhas 397-442)
```python
async def modo_descobrir(page):
    await page.screenshot(path=str(path), full_page=True)
    inputs = await page.locator("input").all()
    for inp in inputs:
        ...
        print(f"    <input id='{id_attr}' name='{name_attr}' ...>")
```
**Explicação:** navega ao PUSH, tira screenshot da página inteira, lista todos os `<input>`, `<textarea>` e `<button>` visíveis com seus IDs.
**Analogia:** mapa de vistoria — andar pelo prédio todo anotando nome de cada sala e número de porta, pra quando precisar voltar saber onde ir.
**Por que importa:** quando o PJe muda layout e os SELETORES da configuração param de funcionar, rodar `--descobrir` mostra quais seletores novos colocar no código.

---

## Bloco 10 — Loop principal + detecção de sessão expirada + relatório (linhas 449-555)
```python
for i, p in enumerate(processos, 1):
    resultado = await incluir_processo(page, p["cnj"], p["observacao"])
    resultados[resultado] += 1
    ...
    url_atual = page.url.lower()
    if "login" in url_atual or "sso" in url_atual:
        log("Sessão expirou! Aguardando re-login...", "AVISO")
        if not await aguardar_login(page):
            break
    await page.wait_for_timeout(2000)  # rate limiting
```
**Explicação:** percorre a lista, inclui um por um, a cada ciclo verifica se não caiu no login de novo (sessão expirou). Pausa 2 segundos entre cada pra não sobrecarregar o PJe. No final, salva um JSON com estatísticas.
**Analogia:** consultas em série — atende paciente, anota no prontuário, confere se o sistema não pediu senha de novo, respira, chama o próximo.
**Por que importa:** sessão do PJe cai depois de alguns minutos. Sem essa checagem, o script continuaria "incluindo" no vazio e marcaria todos como erro.

---

## Como rodar
```bash
# Testar sem mexer em nada (mostra o que faria)
python3 incluir_push.py --dry-run

# Incluir só 3 (teste em produção)
python3 incluir_push.py --limite 3

# Incluir tudo
python3 incluir_push.py

# Incluir um específico
python3 incluir_push.py --cnj 5022119-66.2024.8.13.0024

# Investigar a página (quando PJe muda)
python3 incluir_push.py --descobrir

# Usar Chromium próprio (ignora Chrome aberto)
python3 incluir_push.py --standalone
```

## Erros conhecidos
- **"Campo CNJ não encontrado"** → PJe atualizou HTML. Rodar `--descobrir` e atualizar `SELETORES_CNJ` (linhas 50-59).
- **"Timeout esperando login (5 min)"** → certificado VidaaS não foi inserido a tempo. Rodar de novo.
- **"Sessão expirou"** no meio do lote → normal depois de ~30-60 min. O script tenta re-login automaticamente.
- **"Nenhuma lista de processos encontrada"** → verificar se `LISTA-COMPLETA-PUSH.json` ou `lista-inclusao-push.txt` existe nos caminhos definidos no Bloco 1.
- **Duplicatas contadas como erro** → NÃO é erro. É esperado. Cada processo só pode estar no PUSH uma vez.

## Dependências
- `playwright` (instalar: `pip install playwright && playwright install chromium`)
- Python 3.9+ (usa `asyncio`)

---

Gerado em 2026-04-19 | Revisar a cada mudança estrutural
