# TRF6 — Consulta Pública PJe (1g + 2g) — PENDENTE

Data da análise: 2026-04-19
Investigador: agente de engenharia (Opus 4.7)
Escopo: diagnosticar por que `fonte_pje_trf6` (descobrir_processos.py, linha ~388)
está desabilitada (linhas ~1067-1075) e decidir se dá para reativar por HTTP puro.

## Situação atual

- Função `fonte_pje_trf6` existe e está comentada no `main()` (linha 1075).
- Comentário atual atribui o problema a "form-data diferente (fPP:dpCpf,
  idSelecaoPartePesquisa) e exigência de classe judicial".
- Investigação deste passo mostra que o comentário é PARCIALMENTE incorreto
  (ver "Achados" abaixo). O bloqueio real NÃO é fPP:dpCpf nem classe — é
  outro conjunto de problemas.

## Verificações feitas

### 1. HTTP real dos endpoints

```
curl -skL https://pje1g.trf6.jus.br/pje/ConsultaPublica/listView.seam
→ HTTP=200  size=44217  redirs=1
→ final=https://pje1g.trf6.jus.br/consultapublica/ConsultaPublica/listView.seam

curl -skL https://pje2g.trf6.jus.br/pje/ConsultaPublica/listView.seam
→ HTTP=200  size=44163  redirs=1
→ final=https://pje2g.trf6.jus.br/consultapublica/ConsultaPublica/listView.seam
```

Sem redirect-follow o status é 302 e o corpo tem 255 bytes (página do
redirect). O código em `fonte_pje_trf6` já aponta direto para
`/consultapublica/ConsultaPublica/listView.seam`, então esse não é o
problema (url_base correto).

### 2. Campos de form capturados do HTML real (1g — 2g é idêntico)

Form principal: `<form id="fPP" name="fPP" method="post"
action="/consultapublica/ConsultaPublica/listView.seam;jsessionid=...">`

Hidden do form fPP:

| name                                      | value esperado         |
|-------------------------------------------|------------------------|
| `fPP`                                     | `fPP`                  |
| `autoScroll`                              | `` (vazio)             |
| `fPP:j_idcl`                              | `` (vazio)             |
| `fPP:_link_hidden_`                       | `` (vazio)             |
| `javax.faces.ViewState`                   | `j_id1` no GET inicial |
| `fPP:j_id185:classeProcessualProcessoHidden` | `` (hidden de classe) |

Campos de entrada do usuário:

| name                                                      | função              |
|-----------------------------------------------------------|---------------------|
| `fPP:numProcesso-inputNumeroProcessoDecoration:numProcesso-inputNumeroProcesso` | número CNJ |
| `fPP:j_id158:processoReferenciaInput`                     | proc. referência    |
| `fPP:dnp:nomeParte`                                       | nome da parte       |
| `fPP:j_id176:nomeAdv`                                     | nome do advogado    |
| `fPP:dpDec:documentoParte`                                | **CPF/CNPJ**        |
| `tipoMascaraDocumento`                                    | radio CPF/CNPJ      |
| `mascaraProcessoReferenciaRadio`                          | radio NUN/LIV       |
| `fPP:Decoration:estadoComboOAB`                           | UF OAB              |
| `fPP:Decoration:numeroOAB`                                | nº OAB              |
| `fPP:Decoration:j_id220`                                  | letra OAB (A-Z)     |
| `fPP:searchProcessos`                                     | botão Pesquisar     |

Observação: NÃO existe campo `fPP:dpCpf` no HTML real (o comentário no
código que cita esse nome está errado). O campo de CPF é
`fPP:dpDec:documentoParte` — **igual ao TJMG**. Já é usado no código.

Observação: NÃO existe `idSelecaoPartePesquisa` no HTML público.

Observação: NÃO há obrigatoriedade de classe judicial (o campo
`fPP:j_id185:classeProcessualProcessoHidden` existe mas aceita vazio).

### 3. Achado crítico: reCAPTCHA

O botão Pesquisar tem:

```html
<input ... id="fPP:searchProcessos" name="fPP:searchProcessos"
       onclick="return executarReCaptcha();;A4J.AJAX.Submit('fPP',event,{
           'similarityGroupingId':'fPP:searchProcessos',
           'actionUrl':'/consultapublica/ConsultaPublica/listView.seam;jsessionid=...',
           'parameters':{'fPP:searchProcessos':'fPP:searchProcessos'}
       });return false;"
       value="Pesquisar" type="button" />
```

Três bloqueios reais:

1. **reCAPTCHA obrigatório** (`executarReCaptcha()` antes do submit).
   O POST sem token g-recaptcha-response é rejeitado ou devolve página
   sem resultados — compatível com o bug histórico "retorna CNJs
   aleatórios" (quando o servidor devolve uma página de erro/estado
   anterior, a regex `RE_CNJ` varre template/JS e pega números soltos).

2. **A4J.AJAX.Submit (RichFaces 3.3.3)** — não é POST form-urlencoded
   simples. O framework serializa estado AJAX próprio. O POST atual do
   código bate no endpoint normal (`listView.seam`), mas o servidor
   espera partial-submit do RichFaces com headers específicos.

3. **jsessionid na URL do action** — cada GET gera sessão nova. Enviar
   POST para `/consultapublica/ConsultaPublica/listView.seam` sem
   jsessionid correspondente pode resetar contexto e devolver página
   inicial (também compatível com o bug histórico).

### 4. DataJud TRF6 já está coberto

Em `descobrir_processos.py`:

- Linha 253: `tribunal = "trf6"` detectado pelo segmento do CNJ.
- Linha 819: `tribunal = "trf6" if ".4.06." in cnj else "tjmg"` na validação.
- Linha 824: `for t in ["trf6", "tjmg", "trt3"]` no fallback.
- Config: `config_pje.DATAJUD_ENDPOINTS['trf6']` =
  `https://api-publica.datajud.cnj.jus.br/api_publica_trf6/_search`.

Conclusão: **DataJud TRF6 JÁ é consultado** para enriquecer e validar
CNJs federais. Mas DataJud não descobre CNJs novos por CPF de parte
(só aceita queries por CNJ, classe, órgão etc.). Para **descobrir**
novos CNJs TRF6, a única via sem login seria:

- a) Consulta Pública PJe TRF6 (bloqueada por reCAPTCHA — é este arquivo)
- b) DJEN/Comunica PJe com `siglaTribunal=TRF6` (JÁ coberto em
  `fonte_comunica_pje`, linhas 599-674, DJEN_TRIBUNAIS inclui "TRF6")

## Por que não reescrevi a função

A diretiva explícita da sessão é **não melhorar/augmentar código de
scraping** — apenas analisar. Não foi feita alteração em
`descobrir_processos.py` nem criada função substituta.

## O que falta para reativar (se desejado no futuro)

1. Capturar POST real via DevTools (Network tab) do Chrome durante
   busca manual com CPF, incluindo:
   - Token `g-recaptcha-response` (válido ~2 min).
   - Todos os headers A4J (`Faces-Request: partial/ajax`,
     `X-Requested-With: XMLHttpRequest`, cookie JSESSIONID).
   - Valor real de `javax.faces.ViewState` pós-GET (não `j_id1`).
   - Payload completo (form-urlencoded ou multipart conforme DevTools).

2. Reimplementar com Selenium/Playwright no Chrome debug (porta 9223,
   perfil isolado — padrão do projeto, ver project_download_pje_139.md)
   em vez de requests puro. reCAPTCHA v2/v3 não é contornável sem
   navegador real.

3. Validar com CPF conhecido (127.858.856-60) e verificar se os CNJs
   retornados realmente contêm "JESUS EDUARDO" nas partes via DataJud
   antes de aceitar.

## Recomendação

**Manter desabilitado.** Cobertura de descoberta TRF6 atual via DJEN
(fonte_comunica_pje) é suficiente para perícias ativas (intimações
sempre passam pelo DJEN). Consulta Pública TRF6 só adicionaria
processos sem movimentação recente — baixo valor, custo alto
(Selenium + reCAPTCHA).
