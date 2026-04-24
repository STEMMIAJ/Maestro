---
nome: pipeline-geracao-peticao
entrada: _dados/FICHA.json + tipo da petição (aceite|agendamento|disponibilidade|esclarecimentos|escusa|proposta|prorrogacao|requisicao)
saida: peticoes-geradas/<YYYY-MM-DD>-<tipo>.md + peticoes-geradas/<YYYY-MM-DD>-<tipo>.pdf (timbrado)
duracao_estimada: 1-3 min
agentes_envolvidos: [peticao-identificador, peticao-extrator, peticao-montador, peticao-verificador, peticao-gerador-pdf]
---

# Pipeline 2 — Geração de Petição

## Objetivo

Gerar petição pericial formalmente correta, timbrada e pronta para protocolo, a partir de `FICHA.json` + tipo. **Zero redação livre**: sempre template + dados. O pipeline existe justamente para garantir que o perito nunca escreva manualmente e nunca erre nome/CNJ/valor.

## Pré-requisitos

- `01-CASOS-ATIVOS/<numero-cnj>/_dados/FICHA.json` válido (Pipeline 1 concluído).
- Pasta `peticoes-geradas/` existente no caso (criar se ausente).
- Templates em `/Users/jesus/Desktop/STEMMIA Dexter/MODELOS PETIÇÕES PLACEHOLDERS/<tipo>/` acessíveis.
- Timbrado PDF/imagem em local fixo do sistema (referência no agente `peticao-gerador-pdf`).
- Agentes `peticao-identificador`, `peticao-extrator`, `peticao-montador`, `peticao-verificador`, `peticao-gerador-pdf` disponíveis.
- Tipo informado deve bater com subpasta existente em `MODELOS PETIÇÕES PLACEHOLDERS/`.

## Passos

### 1. Validação de entrada
- **Ação**: conferir que `FICHA.json` existe, é JSON válido, e tipo está em {aceite, agendamento, disponibilidade, esclarecimentos, escusa, proposta, prorrogacao, requisicao}.
- **Tool**: `Bash` (`python3 -m json.tool`, `ls`).
- **Sucesso**: JSON válido + tipo existe como pasta em `MODELOS PETIÇÕES PLACEHOLDERS/`.

### 2. Identificação do template exato
- **Ação**: dentro de `MODELOS PETIÇÕES PLACEHOLDERS/<tipo>/`, escolher o template correto (há variações por subtipo: ex. proposta-simples vs proposta-com-exame-complementar).
- **Agente**: `peticao-identificador` — recebe `FICHA.json` + tipo, devolve caminho absoluto do template.
- **Tool**: `Task`.
- **Lê**: `FICHA.json`, `MODELOS PETIÇÕES PLACEHOLDERS/<tipo>/*.md`, `MODELOS PETIÇÕES PLACEHOLDERS/INDICE.md`.
- **Escreve**: `peticoes-geradas/.tmp/template-escolhido.txt` (path + razão da escolha).
- **Sucesso**: arquivo aponta para template existente e legível.

### 3. Extração de placeholders
- **Ação**: ler template, listar todos os placeholders `{{VARIAVEL}}`.
- **Agente**: `peticao-extrator`.
- **Tool**: `Task` (`Grep` interno para `\{\{[A-Z_]+\}\}`).
- **Escreve**: `peticoes-geradas/.tmp/placeholders.json` — lista `{variavel, origem_no_FICHA, valor, status}`.
- **Sucesso**: toda variável tem `origem_no_FICHA` mapeada OU `status=pendente` explícito.

### 4. Preenchimento determinístico
- **Ação**: substituir cada `{{VARIAVEL}}` pelo valor correspondente. Valores monetários: sempre acompanhados do por extenso (campo `honorarios.por_extenso` da FICHA).
- **Agente**: `peticao-montador`.
- **Tool**: `Task` (Read + Write).
- **Lê**: template + `placeholders.json`.
- **Escreve**: `peticoes-geradas/<YYYY-MM-DD>-<tipo>.md` (ainda não timbrado).
- **Sucesso**: zero `{{...}}` remanescente no arquivo de saída (`grep -c '{{' = 0`).

### 5. Verificação anti-erro
- **Ação**: checar manualmente 5 pontos críticos:
  1. CNJ exato igual ao da FICHA.
  2. Nome do autor sem erro de grafia.
  3. Valor em algarismos + por extenso concordantes.
  4. Data no formato correto (`DD de MMMM de AAAA` por extenso).
  5. Vara/comarca corretas.
- **Agente**: `peticao-verificador`.
- **Tool**: `Task` (Grep + comparação com FICHA).
- **Escreve**: `peticoes-geradas/.tmp/verificacao-<data>-<tipo>.json` com `{criterio, ok, evidencia}`.
- **Sucesso**: todos os 5 critérios retornam `ok: true`. Qualquer `false` ⇒ abortar e corrigir template/FICHA.

### 6. Geração de PDF timbrado
- **Ação**: converter `.md` em `.pdf` aplicando timbrado (cabeçalho com nome, CRM, endereço pericial; rodapé com página X de Y).
- **Agente**: `peticao-gerador-pdf`.
- **Tool**: `Task` (pandoc/weasyprint ou equivalente interno do agente).
- **Lê**: `.md` + imagem/PDF de timbrado.
- **Escreve**: `peticoes-geradas/<YYYY-MM-DD>-<tipo>.pdf`.
- **Sucesso**: PDF existe, ≥1 página, tamanho >5 KB, timbrado visível na página 1.

### 7. Registro final
- **Ação**: registrar no `_dados/HISTORICO-PETICOES.md` (tabela: data, tipo, arquivo, protocolada sim/não).
- **Tool**: `Edit`.
- **Sucesso**: nova linha adicionada.

## Pontos de verificação

| # | Checagem | Comando | Esperado |
|---|----------|---------|----------|
| V1 | MD sem placeholders órfãos | `grep -c '{{' peticoes-geradas/<data>-<tipo>.md` | 0 |
| V2 | CNJ no MD bate com FICHA | `grep numero_cnj _dados/FICHA.json` vs `grep <cnj> MD` | igual |
| V3 | Valor por extenso presente quando há valor | `grep -E 'R\$' MD && grep -Ei '(reais|centavos)' MD` | ambos ou nenhum |
| V4 | PDF existe e >5 KB | `ls -la peticoes-geradas/<data>-<tipo>.pdf` | size ≥5000 |
| V5 | PDF tem texto extraível (não é só imagem) | `pdftotext PDF - \| wc -c` | ≥500 |
| V6 | `verificacao-<data>-<tipo>.json` com todos `ok:true` | `jq '.[] \| select(.ok==false)' verif.json` | vazio |
| V7 | `HISTORICO-PETICOES.md` atualizado | `tail -1 _dados/HISTORICO-PETICOES.md` | contém tipo+data |

Só declarar “feito” após V1–V7 OK.

## Erros comuns + fix

1. **Placeholder sem correspondente na FICHA** (`{{NOME_PERITO_AUXILIAR}}` em template de proposta conjunta, mas FICHA só tem perito único) → tratar em `peticao-extrator`: se não existe no schema, marcar `status=opcional` e remover a linha/bloco condicional do template, ou preencher com valor-padrão do perfil do perito.
2. **Valor em extenso errado** (“seiscentos reais” para R$ 650) → nunca derivar do número em tempo real; usar sempre `FICHA.honorarios.por_extenso`. Se divergente, abortar e corrigir FICHA primeiro.
3. **Timbrado cortado ou em página errada** → conferir margens do template (`margin-top` ≥ 3 cm). Regenerar PDF.
4. **CNJ com máscara diferente** (com/sem pontos) → normalizar no `peticao-montador` para formato padrão `NNNNNNN-DD.AAAA.J.TR.OOOO`.
5. **Acentuação perdida no PDF** → conferir encoding do pandoc (`--pdf-engine=xelatex` ou weasyprint com UTF-8). Nunca aceitar PDF com “cora��o”.

## Exemplo executado — caso 0000000-00.0000.0.00.0000, tipo `proposta`

1. FICHA existe. Tipo `proposta` válido.
2. `peticao-identificador` escolhe `MODELOS PETIÇÕES PLACEHOLDERS/proposta/proposta-padrao-INSS.md` (razão: tipo_acao = “Auxílio-doença”).
3. `peticao-extrator` encontra 9 placeholders: `{{CNJ}}`, `{{VARA}}`, `{{COMARCA}}`, `{{AUTOR_NOME}}`, `{{AUTOR_CPF}}`, `{{VALOR_HONORARIOS}}`, `{{VALOR_EXTENSO}}`, `{{DATA_PETICAO}}`, `{{CID_PRINCIPAL}}`.
4. `peticao-montador` preenche: `{{CNJ}}` → `0000000-00.0000.0.00.0000`, `{{AUTOR_NOME}}` → `Fulano de Tal`, `{{VALOR_HONORARIOS}}` → `R$ 600,00`, `{{VALOR_EXTENSO}}` → `seiscentos reais`, `{{DATA_PETICAO}}` → `20 de abril de 2026`, `{{CID_PRINCIPAL}}` → `M54.5`. Salva `peticoes-geradas/2026-04-20-proposta.md`.
5. `peticao-verificador` confirma os 5 critérios. JSON de verificação: tudo `ok:true`.
6. `peticao-gerador-pdf` produz `peticoes-geradas/2026-04-20-proposta.pdf` (2 páginas, 87 KB, timbrado OK).
7. `HISTORICO-PETICOES.md` recebe linha: `2026-04-20 | proposta | 2026-04-20-proposta.pdf | pendente-protocolo`.
8. V1–V7 passam. Pipeline 2 concluído em 1 min 38 s.
