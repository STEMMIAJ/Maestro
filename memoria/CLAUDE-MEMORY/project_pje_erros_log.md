---
name: Log de erros PJe download
description: Registro de TODOS os erros encontrados durante execuções do baixar_push_pje.py. Atualizado a cada execução.
type: project
originSessionId: 98656b59-fc0f-45d9-8f00-858ac201e9a9
---
# Log de Erros — Download PJe TJMG

---

## Execução 1 — 2026-04-13 05:54–05:57

**Resultado**: 5 baixados, 26 erros
**Relatório JSON**: `C:\Users\jesus\Desktop\processos-pje\relatorio-20260413-055737.json`

### Processos com sucesso (5)
- [1] a [4]: "Já baixado" (sessões anteriores)
- [5] 5022119-66.2024.8.13.0105: DOWNLOAD encontrado (texto='DOWNLOAD'), download completou

### Erro: "CNJ não encontrado na tabela (total linhas: 65)"
- Afetou processos [6] a [31] (26 processos)
- **Causa raiz**: Processo [5] abriu Autos Digitais na MESMA aba. Após download, aba_push ficou na página do processo, NÃO na lista PUSH.
- **Fix aplicado**: variável `opened_same_tab` + `navegar_para_push()` após download em mesma aba

---

## Execução 2 — 2026-04-13 06:02–06:17 (com fix opened_same_tab)

**Fix aplicado**: `opened_same_tab` + `navegar_para_push()` após fechar_abas_extras

### Processos com sucesso
- [1] a [5]: "Já baixado" (sessões anteriores)
- [6] 5016125-49.2023.8.13.0701: SALVO (28159 KB, 184.7s) — mesma aba, FIX FUNCIONOU (voltou ao PUSH em 26.4s)
- [7] 5011972-13.2025.8.13.0471: SALVO (28159 KB, 187.6s) — mesma aba, FIX FUNCIONOU

### Erro NOVO: Loop infinito baixando mesmo processo
- **Evidência**: 14 PDFs na pasta, mas 7 são duplicatas de 5001702-49.2024.8.13.0184 com hashes diferentes
- Arquivos duplicados: `5001702-49.2024.8.13.0184-1776069151062-1476830-processo.pdf` (7 cópias)
- Python ainda rodando às 06:18 mas sem output novo no CMD
- Chrome mostrando about:blank
- **Causa raiz provável**: Após navegar_para_push(), a tabela é re-extraída pelo main loop mas o script re-processa os mesmos CNJs da lista original (não re-extrai). O dedup check `destino.exists()` falha porque o arquivo baixado tem nome PJe original (hash), não o nome sanitizado {CNJ}.pdf
- **OU**: O navegar_para_push() não está voltando para a mesma posição da tabela — a re-extração pega processos diferentes, e o loop principal não sabe que já processou esses CNJs
- **Fix necessário**: 
  1. O main loop precisa re-extrair processos após cada volta ao PUSH (já faz isso no início do while)
  2. O dedup precisa ser mais robusto — verificar se QUALQUER arquivo com o CNJ existe (não só {CNJ}.pdf exato)
  3. OU: manter um set() de CNJs já processados nesta execução para evitar reprocessamento

### Botões mapeados (pedido do usuário)
Todos os botões/seletores que o script usa no fluxo PJe:

1. **Link PUSH**: `By.LINK_TEXT "PUSH"`, `By.PARTIAL_LINK_TEXT "PUSH"`, `By.XPATH "//a[normalize-space(text())='PUSH']"`, `By.CSS_SELECTOR "a[href*='Push']"`
2. **Botão Autos Digitais**: `row.find_elements(By.TAG_NAME, "a")` → filtrado por title contendo "auto/digital/visualizar/abrir" ou href contendo "autos/processo/visualiz"
3. **Ícone Download Autos**: `By.CSS_SELECTOR "a[title], button[title], span[title]"` → filtrado por title "download autos"; fallback: `.fa-download, [class*='download']`
4. **Iframe**: `By.TAG_NAME "iframe"` → switch_to.frame() → verifica se tem buttons/inputs/links/selects
5. **Dropdowns (Incluir expediente/movimentos)**: `By.TAG_NAME "select"` → Select() → se "Não" → muda para "Sim"
6. **Botão DOWNLOAD final** (5 estratégias):
   - E1: `By.CSS_SELECTOR "button, input[type='submit'], input[type='button'], a"` → texto "DOWNLOAD/BAIXAR/GERAR PDF/GERAR/OK"
   - E2: `By.CSS_SELECTOR "[title*='ownload'], [title*='aixar'], [title*='erar']"`
   - E3: XPath translate: `//button[contains(translate(...), 'DOWNLOAD')]`, idem BAIXAR, idem input, idem link
   - E4: Classes PJe: `.btn-primary, .btn-info, .btn-success, .rf-bt, .rich-btn`
   - E5: `By.CSS_SELECTOR "input[type='submit']"` visível
7. **Paginação**: `By.LINK_TEXT ">"` ou `"»"`
8. **Tabela PUSH**: `By.CSS_SELECTOR "table tbody tr"` (extração) e `"table tr, .rich-table-row, .rf-dt-r, tr"` (fallback)

---
