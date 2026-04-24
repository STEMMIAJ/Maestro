# README — Fonte TRF6 (descoberta de processos)

Data: 2026-04-19
Status: **fonte_pje_trf6 permanece DESABILITADA**

## Situação atual

- `descobrir_processos.py::fonte_pje_trf6` (linha ~388) está comentada
  em `main()` (linha ~1075) desde o plano binary-gliding-pine.
- Motivo original registrado: "retorna CNJs aleatórios".
- Esta investigação (2026-04-19) confirmou o problema e identificou
  **três causas combinadas** em vez de uma só.

## O que foi investigado

1. **Leitura da função**: `descobrir_processos.py` linhas 388-462.
2. **HTTP real** dos endpoints `pje1g.trf6.jus.br` e `pje2g.trf6.jus.br`
   (ConsultaPublica/listView.seam) — seguindo redirect 302 → 200, HTML
   ~44 KB.
3. **Extração completa** dos nomes de campos `<input>` e `<form>` via
   curl + grep.
4. **Grep no repositório** para confirmar cobertura DataJud TRF6.
5. **Arquivo detalhado**: `trf6_pendente.md` (este diretório) tem o
   dump completo de campos, ViewState e evidências.

## O que falhou no código atual

Citando o comentário do código (linha 1070): afirma que o form usa
`fPP:dpCpf` e `idSelecaoPartePesquisa`. **Esses nomes NÃO existem no
HTML real do TRF6.** O campo correto é `fPP:dpDec:documentoParte` —
idêntico ao TJMG — e já está no payload da função. Portanto o
comentário está desatualizado/incorreto.

O bloqueio real é outro:

- **reCAPTCHA obrigatório** no botão Pesquisar
  (`onclick="return executarReCaptcha();..."`). HTTP simples sem token
  g-recaptcha-response não passa.
- **RichFaces 3.3.3 A4J.AJAX.Submit** — submit é AJAX parcial, não
  form POST clássico. Headers específicos exigidos.
- **jsessionid no action do form** — sessão precisa bater com cookie.

O bug "CNJs aleatórios" é consistente com a regex `RE_CNJ.findall` varrer
uma página de erro/template (números de exemplo em máscara, processos
mock em JS) quando o servidor devolve resposta degradada.

## Cobertura atual de TRF6 sem a fonte Consulta Pública

| Fonte                  | Status | Arquivo                     |
|------------------------|--------|-----------------------------|
| DataJud TRF6 (enriquec)| ATIVO  | descobrir_processos.py:209  |
| DataJud TRF6 (valida)  | ATIVO  | descobrir_processos.py:819  |
| DJEN / Comunica PJe    | ATIVO  | descobrir_processos.py:640  |
| PJe Consulta Pública   | OFF    | descobrir_processos.py:388  |

Intimações reais (que é o que importa para prazos) passam pelo DJEN com
`siglaTribunal=TRF6` → já são capturadas por `fonte_comunica_pje`.

## Recomendação (3 opções)

### Opção A — Manter desabilitado (recomendado)

- Cobertura via DJEN + DataJud é suficiente para perícias ativas.
- Zero esforço, zero risco de poluir CNJs com homônimos.
- Processos sem movimentação recente ficam fora — aceitável, pois
  sistema é para ação pericial, não para arqueologia.

### Opção B — Reescrever com Selenium/Chrome debug

- Reaproveitar perfil isolado + porta 9223 já usada no fluxo de
  download (ver `project_download_pje_139.md`).
- Abrir Consulta Pública TRF6, preencher CPF, resolver reCAPTCHA
  manualmente na primeira execução do dia (token fica em cookie),
  extrair CNJs do DOM `fPP:processosTable`.
- Custo: 1-2h. Valor: marginal (só adiciona processos sem intimação
  recente).

### Opção C — Capturar POST via DevTools e replicar em requests

- Abrir DevTools > Network durante busca manual.
- Copiar como cURL o POST resultante (traz g-recaptcha-response,
  ViewState real, todos os headers A4J).
- Replicar em Python. **Problema**: token reCAPTCHA expira em ~2 min,
  então a cada execução precisa captura manual. Inviável para cron.
- Não recomendado.

## Arquivos desta investigação

- `/Users/jesus/Desktop/STEMMIA Dexter/src/pje/descoberta/fontes/trf6_pendente.md`
  — diagnóstico técnico completo, campos, payload, evidências.
- `/Users/jesus/Desktop/STEMMIA Dexter/src/pje/descoberta/fontes/README-trf6.md`
  — este arquivo.
- `/Users/jesus/Desktop/STEMMIA Dexter/src/pje/_logs/erros_fluxo.jsonl`
  — entrada de log do problema.
