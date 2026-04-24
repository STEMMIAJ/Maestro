# descobrir_processos.py — Descoberta automática de processos do perito

## O que esse fluxo faz (1 frase)
Consulta 6 fontes públicas e privadas (DJe, DataJud, PJe Consulta Pública, Portal TJMG, DJEN CNJ, AJ/AJG) em paralelo, cruza o que achou com a lista local, valida os CNJs novos, e gera um CSV consolidado + cria pastas prontas para download.

## Arquitetura da pasta
```
descoberta/
├── descobrir_processos.py     (1234 linhas — orquestrador)
├── core/
│   └── filtro_perito.py        (lógica auxiliar para distinguir homônimos)
├── fontes/
│   └── consulta_publica_tjmg.py  (módulo isolado de uma fonte específica)
├── fontes-cache/               (cache de respostas HTTP das fontes)
├── consolidado/                (CSVs e JSONs consolidados, saída final)
├── logs/                       (logs de cada execução)
└── blacklist_manual.txt        (CNJs a ignorar manualmente)
```

---

## Bloco 1 — Constantes do perito e das APIs (linhas 47-75)
```python
PERITO_CPF = "12785885660"
PERITO_CPF_FMT = "127.858.856-60"
PERITO_NOME = "NOLETO"
DATAJUD_KEY = "cDZHYzlZa0JadVREZDJCendQbXY6..."
DATAJUD_ENDPOINTS = {
    "tjmg": "https://api-publica.datajud.cnj.jus.br/api_publica_tjmg/_search",
    "trf6": "https://api-publica.datajud.cnj.jus.br/api_publica_trf6/_search",
    ...
}
```
**Explicação:** identidade do perito (CPF, sobrenome), chave pública do DataJud (API do CNJ) e URLs dos tribunais.
**Analogia:** crachá e chaveiro — sem eles você não entra em lugar nenhum. O CPF é o "crachá", a DATAJUD_KEY é a chave do arquivo digital.
**Por que importa:** se trocar de perito ou adicionar outro tribunal, é aqui que mexe. Chave DATAJUD é pública (do CNJ), não é segredo.

---

## Bloco 2 — Carregar CNJs já conhecidos (linhas 102-135)
```python
def carregar_cnjs_conhecidos():
    cnjs = set()
    for pasta in PROCESSOS_DIR.iterdir():
        ficha = pasta / "FICHA.json"
        if ficha.exists():
            data = json.loads(ficha.read_text(encoding="utf-8"))
            cnj = data.get("cnj") or data.get("numero_cnj") ...
            if RE_CNJ.match(cnj):
                cnjs.add(cnj)
    ...
    return cnjs
```
**Explicação:** varre todas as pastas de processos do Dexter e lê o FICHA.json de cada uma pra montar um conjunto com todos os CNJs já trabalhados.
**Analogia:** checar o arquivo morto antes de abrir um caso novo — "esse processo eu já peguei em 2023?".
**Por que importa:** sem isso o script marcaria processos antigos como "novos" todo dia. Esse set é a base de comparação pra decidir o que é realmente novo.

---

## Bloco 3 — FONTE 1: DJe TJMG (jornal oficial eletrônico) (linhas 160-199)
```python
def fonte_dje_tjmg(dias=3):
    from dje_tjmg import buscar_no_diario_html
    for i in range(dias):
        d = hoje - timedelta(days=i)
        matches = buscar_no_diario_html(data_str, modo_descoberta=True)
        for m in matches:
            for cnj in m.get("cnjs_no_contexto", []):
                cnjs_encontrados.add(cnj)
```
**Explicação:** baixa o HTML do Diário de Justiça Eletrônico do TJMG dos últimos N dias, procura o nome do perito no texto, extrai os CNJs que aparecem perto do nome.
**Analogia:** ler o jornal do dia procurando seu nome — "onde fui citado esta semana?".
**Por que importa:** é a fonte mais confiável para nomeações novas. Se o nome do perito sai no diário, 99% é caso novo.

---

## Bloco 4 — FONTE 2: DataJud CNJ (enriquecimento) (linhas 206-279)
```python
def consultar_datajud_cnj(cnj, tribunal="tjmg"):
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"APIKey {DATAJUD_KEY}",
    }, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        hits = data.get("hits", {}).get("hits", [])
        return hits[0].get("_source", {})
```
**Explicação:** para cada CNJ já descoberto, pergunta ao DataJud CNJ: "me dá classe, órgão julgador, grau, total de movimentos desse processo".
**Analogia:** ficha cadastral — você tem o nome do paciente (CNJ), o DataJud preenche o resto (idade, endereço, histórico).
**Por que importa:** enriquece o CSV final com metadados úteis pra priorizar qual processo trabalhar primeiro.

---

## Bloco 5 — FONTE 3: PJe Consulta Pública TJMG (linhas 286-378)
```python
def fonte_pje_consulta_publica():
    resp = session.get(f"{base_url}/pje/ConsultaPublica/listView.seam")
    vs_match = re.search(r'id="javax\.faces\.ViewState"\s+value="([^"]+)"', html)
    view_state = vs_match.group(1)
    data = {
        "fPP:dpDec:documentoParte": PERITO_CPF_FMT,
        "fPP:searchProcessos": "Pesquisar",
        "javax.faces.ViewState": view_state,
        ...
    }
    resp2 = session.post(..., data=data)
    cnjs_raw = RE_CNJ.findall(resp2.text)
```
**Explicação:** entra na consulta pública do PJe TJMG, extrai o ViewState (token de sessão JSF/Seam), submete busca por CPF do perito, parseia os CNJs do HTML de resposta.
**Analogia:** protocolo no balcão — você tem que pegar a senha (ViewState), preencher o formulário e só então entregar. Sem a senha, jogam fora.
**Por que importa:** descobre processos que o perito é parte mas que ainda não saíram no DJe. Sem login. Só funciona enquanto o PJe não muda o formulário.

---

## Bloco 6 — FONTES 3B, 3C: PJe TRF6 e Portal TJMG Unificado (linhas 385-513)
```python
def fonte_pje_trf6():
    for grau, url_base in [
        ("1g", "https://pje1g.trf6.jus.br/consultapublica"),
        ("2g", "https://pje2g.trf6.jus.br/consultapublica"),
    ]:
        ...

def fonte_portal_tjmg():
    url = "https://www.tjmg.jus.br/portal-tjmg/processos/andamento-processual/"
    body = urllib.parse.urlencode({"tipoPesquisa": "2", "cpfCnpj": PERITO_CPF})
```
**Explicação:** mesmo padrão da Fonte 3, mas para Justiça Federal (TRF6, 1º e 2º grau) e para o portal unificado do TJMG que integra PJe + Themis + Projudi.
**Analogia:** consultar em todas as clínicas conveniadas, não só na principal — paciente pode ter prontuário em várias.
**Por que importa:** processos federais (previdenciário, INSS) não aparecem no PJe TJMG. Portal unificado pega o que está em sistemas antigos (Themis, Projudi).
**Nota:** `fonte_pje_trf6` está DESABILITADA no main (linha 1061) porque estava retornando CNJs aleatórios — `TODO` pendente.

---

## Bloco 7 — FONTE 6: DJEN API pública (Diário Eletrônico CNJ) (linhas 599-695)
```python
DJEN_BASE = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"
DJEN_TRIBUNAIS = ["TJMG", "TRF6"]
DJEN_FILTRO_TEXTO = re.compile(r'PERIT|NOMEADO|LAUDO|EXPERT', re.IGNORECASE)

def _buscar_djen_tribunal(tribunal, nome="JESUS EDUARDO", itens=100):
    params = urllib.parse.urlencode({
        "nomeParte": nome, "siglaTribunal": tribunal, "itensPorPagina": itens,
    })
    ...

def fonte_comunica_pje(dias=30):
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(_buscar_djen_tribunal, trib): trib for trib in DJEN_TRIBUNAIS}
        ...
        for item in items:
            texto = item.get("texto", "").upper()
            if not DJEN_FILTRO_TEXTO.search(texto):
                continue  # descarta homônimos
```
**Explicação:** API nova do CNJ que unifica comunicações/intimações de todos os tribunais. Busca pelo nome, filtra só itens que têm "PERIT"/"NOMEADO"/"LAUDO"/"EXPERT" no texto (elimina homônimos advogado/parte).
**Analogia:** assinatura de clipping — só que o clipping vem pronto do CNJ. E esse clipping tem filtro: só notícia que menciona "cirurgia" (perícia), não qualquer coisa.
**Por que importa:** fonte mais moderna e confiável. CNJs daqui vêm "pré-validados" — pulam a etapa de validação depois (ver Bloco 10 do main).

---

## Bloco 8 — FONTES 4/5: AJ TJMG + AJG Federal (com login) (linhas 520-592)
```python
def fonte_aj_ajg(porta=9223):
    from consultar_aj import conectar_aj, listar_nomeacoes
    page = conectar_aj(porta)
    noms = listar_nomeacoes(page, situacao="TODAS")
    for n in noms:
        cnj = n.get("numero_processo_cnj", "")
        ...
    from consultar_ajg import conectar_ajg, listar_nomeacoes as listar_ajg
    ...
```
**Explicação:** AJ (Assistência Judiciária do TJMG) e AJG (Assistência Judiciária Gratuita Federal) exigem login. Usa Chrome já aberto via CDP (porta 9223) e importa módulos separados que fazem a navegação.
**Analogia:** sistema interno do hospital — precisa ter crachá no leitor pra entrar. O script usa um Chrome que você já abriu.
**Por que importa:** é lá que aparecem os honorários e situação da nomeação (PENDENTE/PAGO). Só roda com `--com-browser`.

---

## Bloco 9 — Validação: confirmar se o perito realmente está no processo (linhas 702-854)
```python
def validar_cnjs_pje(cnjs_novos, max_validacoes=50):
    for cnj in sorted(cnjs_novos)[:max_validacoes]:
        resp2 = sess.post(..., data={"fPP:numProcesso...": cnj_limpo, ...})
        texto = resp2.text.upper()
        if "JESUS EDUARDO" in texto or PERITO_CPF in texto:
            confirmados.add(cnj)
        else:
            descartados.add(cnj)

def validar_cnjs_datajud(cnjs_novos, max_validacoes=50):
    for cnj in sorted(cnjs_novos)[:max_validacoes]:
        dados = consultar_datajud_cnj(cnj, tribunal)
        texto = json.dumps(dados, ensure_ascii=False).upper()
        encontrado = any(t.upper() in texto for t in termos_perito)
```
**Explicação:** para cada CNJ novo, consulta a ficha detalhada do processo e busca o nome/CPF do perito dentro. Se não achar o nome, DESCARTA (não é dele).
**Analogia:** segunda opinião médica — um exame pode dar falso-positivo. Só confia quando dois exames apontam a mesma coisa.
**Por que importa:** fontes retornam falsos-positivos (homônimos, erro de busca). Sem validação, o Dexter acumularia lixo. Limite de 50 evita travar a execução.

---

## Bloco 10 — Reconciliação: cruzar fontes e classificar "novo vs conhecido" (linhas 861-924)
```python
def reconciliar(fontes_resultados, datajud_dados, cnjs_conhecidos):
    todos_cnjs = set(cnjs_conhecidos)
    fonte_por_cnj = {}
    for resultado in fontes_resultados:
        fonte_nome = resultado.get("fonte", "?")
        for cnj in resultado.get("cnjs", []):
            todos_cnjs.add(cnj)
            fonte_por_cnj[cnj].append(fonte_nome)
    novos = todos_cnjs - cnjs_conhecidos
    ...
```
**Explicação:** junta todos os CNJs de todas as fontes num conjunto único, registra de qual fonte cada CNJ veio, separa "novos" (não estão no Dexter) dos "conhecidos".
**Analogia:** reunião clínica — 3 médicos avaliaram o mesmo paciente. Consolida os achados num laudo único que mostra "quem viu o quê".
**Por que importa:** mostra confiabilidade — um CNJ em 3 fontes é mais confiável que em 1. Base do CSV final.

---

## Bloco 11 — Geração de CSV + criação de pastas para novos + pendentes (linhas 931-1008)
```python
def gerar_csv(consolidado):
    csv_path = CONSOLIDADO_DIR / f"RELATORIO_PROCESSOS_{data_str}.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writerows(processos)

def criar_pastas_novos(novos_cnjs, datajud_dados):
    for cnj in novos_cnjs:
        pasta = PROCESSOS_DIR / cnj
        pasta.mkdir(parents=True, exist_ok=True)
        (pasta / "FICHA.json").write_text(json.dumps(ficha, ...))

def atualizar_pendentes(novos_cnjs):
    pendentes.append(cnj)
    PENDENTES_JSON.write_text(json.dumps(pendentes, ...))
```
**Explicação:** três entregáveis finais: (1) CSV consolidado pra abrir no Excel, (2) pasta vazia com FICHA.json para cada novo CNJ, (3) lista `_pendentes_download.json` que o script de download lê depois.
**Analogia:** saída da consulta — (1) receita pro paciente, (2) abre prontuário novo no sistema, (3) agenda retorno.
**Por que importa:** conecta este fluxo com o próximo (download). Cria o "TO-DO" pro `baixar_push_pje.py`.

---

## Bloco 12 — Orquestração principal (paralelo) (linhas 1015-1230)
```python
def main():
    cnjs_conhecidos = carregar_cnjs_conhecidos()
    fontes_resultados = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures[pool.submit(fonte_dje_tjmg, args.dias)] = "dje_tjmg"
        futures[pool.submit(fonte_pje_consulta_publica)] = "pje_tjmg"
        futures[pool.submit(fonte_portal_tjmg)] = "portal_tjmg"
        futures[pool.submit(fonte_comunica_pje, args.dias)] = "comunica_pje"
        for future in as_completed(futures):
            resultado = future.result()
            fontes_resultados.append(resultado)
    ...
    # Valida novos, reconcilia, gera CSV, cria pastas, notifica Telegram
```
**Explicação:** dispara 4 fontes em paralelo (ThreadPool com 6 workers), coleta resultado de todas, enriquece com DataJud, valida, reconcilia, salva tudo.
**Analogia:** quatro auxiliares vão a quatro cartórios ao mesmo tempo — quando todos voltam, você junta as informações.
**Por que importa:** rodar em paralelo reduz 6 minutos de busca sequencial pra ~1:30min.

---

## Como rodar
```bash
# Só fontes públicas (rápido, sem login)
python3 descobrir_processos.py --sem-browser

# Últimos 7 dias do DJe
python3 descobrir_processos.py --sem-browser --dias 7

# Tudo, incluindo AJ/AJG (precisa Chrome logado na porta 9223)
python3 descobrir_processos.py --com-browser

# Backfill DJe 2 anos (demora)
python3 descobrir_processos.py --backfill 730

# Saída JSON + salvar tudo em disco
python3 descobrir_processos.py --sem-browser --json --salvar

# Pular enriquecimento DataJud (mais rápido)
python3 descobrir_processos.py --sem-browser --skip-datajud
```

## Erros conhecidos
- **"ViewState não encontrado"** → PJe mudou o formulário. Atualizar a regex nas funções `fonte_pje_consulta_publica` / `validar_cnjs_pje`.
- **`requests não instalado`** → `pip install requests`.
- **"DJEN rate limited (429)"** → script espera 60s e tenta de novo. Não precisa intervenção.
- **`fonte_pje_trf6` retorna CNJs aleatórios** → desabilitada no main (linha 1061). TODO pendente.
- **"AJ TJMG: ..."** erros → Chrome não está rodando em `--remote-debugging-port=9223`.
- **DataJud timeout** → API do CNJ instável às vezes. Rodar com `--skip-datajud`.

## Dependências
- Python 3.9+ (stdlib: `urllib`, `ssl`, `json`, `re`, `csv`, `concurrent.futures`)
- `requests` (opcional — para PJe Consulta Pública via POST JSF)
- Módulo local `monitor-publicacoes/dje_tjmg.py` (importado em runtime)
- Módulos locais `consultar_aj.py` e `consultar_ajg.py` (se usar `--com-browser`)

---

Gerado em 2026-04-19 | Revisar a cada mudança estrutural
