# PLANO — Extração de templates a partir das peças reais do Dr. Jesus

**Criado:** 2026-04-20
**Regra zero:** nenhum template é criado sem peça real do perito como base. Violação = refazer.

---

## Princípio fundamental: separar INVARIANTE de VARIANTE

Toda petição pericial do Dr. Jesus tem:

### Partes INVARIANTES (iguais em todas — vão em `02-BIBLIOTECA/clausulas-padrao/`)
- **endereçamento** — `AO JUÍZO DA {{juizo.numero_vara}}ª VARA {{juizo.materias}} DA COMARCA DE {{juizo.comarca}} – {{juizo.uf}}`
- **identificador-processo** — `Processo nº: {{processo.cnj}}`
- **vocativo** — `Meritíssimo Juiz,`
- **fecho** — `Termos em que,\nPede deferimento.`
- **assinatura** — 3 linhas (nome / função-CRM / filiação ABMLPM)
- **data-local** — `{{data.por_extenso}}, Governador Valadares - MG.`

Essas 6 cláusulas viram arquivos MD separados em `02-BIBLIOTECA/clausulas-padrao/` e são INCLUÍDAS nos templates por referência (via mecanismo a definir — ver Fase 4 abaixo).

### Partes VARIANTES (mudam por subtipo — ficam dentro do `TEMPLATE.md` de cada um)
- **título da manifestação** (`ACEITE DE ENCARGO`, `AGENDAMENTO DE PERÍCIA`, etc.)
- **corpo/argumentação** específico do subtipo
- **placeholders específicos** (honorários, data/hora da perícia, motivos da escusa, etc.)

---

## Fase 1 — RECEPÇÃO dos documentos reais

**Quando:** Dr. Jesus baixa e disponibiliza PDFs/DOCX.

**Onde o usuário deposita:**
```
cowork/02-BIBLIOTECA/peticoes/_fonte-originais-perito/
├── aceite/                    (3 DOCX já presentes — fonte dos 3 templates ativos)
├── escusa/                    (aguardando)
├── proposta-honorarios/
│   ├── civel-dano-pessoal/   (aguardando)
│   ├── erro-medico/          (aguardando)
│   ├── securitario/          (aguardando)
│   ├── previdenciario/       (aguardando)
│   ├── trabalhista/          (aguardando)
│   └── dpvat/                (aguardando)
├── esclarecimento/            (aguardando)
├── majoracao-honorarios/      (aguardando)
├── impugnacao-quesitos/       (aguardando)
├── complementar/              (aguardando)
└── mutirao/                   (aguardando)
```

E para laudos / respostas:
```
cowork/02-BIBLIOTECA/laudos/_fonte-originais-perito/{6 classes}/
cowork/02-BIBLIOTECA/respostas/_fonte-originais-perito/{3 tipos}/
```

**Quantidade ideal por subtipo:**
- 1 peça → dá para extrair template, mas sem detectar variações
- 2-3 peças → ideal (identifica o que é fixo vs. o que muda caso a caso)
- 5+ peças → muito bom (permite detectar 2ª ordem: vocabulário alternativo, frases condicionais)

---

## Fase 2 — EXTRAÇÃO do texto cru

Para cada peça real recebida:

1. **Se DOCX:** usar `python -m zipfile -e arquivo.docx /tmp/extracted/` + `docx2txt` ou regex no `word/document.xml` para extrair texto limpo. Verificar acentuação UTF-8.
2. **Se PDF:** usar `pdftotext -layout arquivo.pdf -` e preservar quebras.
3. Salvar texto extraído ao lado do DOCX original: `arquivo.txt` (mesmo basename).
4. Se houver imagens incorporadas (timbrado, assinatura) → `word/media/` → mover para `03-IDENTIDADE/` se ainda não estiverem lá.

**Script a criar:** `05-AUTOMACOES/scripts/extrair_texto_docx.py` (atualmente não existe, mas o padrão já foi usado manualmente nos 3 primeiros DOCX).

---

## Fase 3 — ANÁLISE comparativa dentro do subtipo

Quando houver ≥2 peças do mesmo subtipo:

1. **Diff parágrafo a parágrafo** entre as peças → identifica trechos idênticos (candidatos a INVARIANTE local do subtipo) vs. trechos que mudam (candidatos a PLACEHOLDER).
2. **Classificar cada trecho que muda:**
   - Número de processo, IDs, vara, comarca → placeholder simples `{{path}}`
   - Lista de IDs → `{{#lista:path}}`
   - Motivos/justificativas que aparecem em algumas peças mas não em outras → bloco condicional `{{#se:path}}...{{/se}}`
   - Dados pessoais do autor/réu → estruturar em `partes.autor.*` e `partes.reu.*`
3. **Mapear invariantes locais** (frases/parágrafos iguais em todas as peças do subtipo) → corpo fixo do `TEMPLATE.md`.
4. **Mapear invariantes globais** (que coincidem com cláusulas-padrão já extraídas) → substituir por referência à cláusula-padrão.

**Output dessa fase (por subtipo):**
```
cowork/02-BIBLIOTECA/peticoes/<subtipo>/_analise.md
```
contendo: lista de placeholders identificados, blocos condicionais detectados, invariantes locais, invariantes globais reutilizados.

---

## Fase 4 — MONTAGEM do TEMPLATE.md

Para cada subtipo:

1. Criar `02-BIBLIOTECA/peticoes/<subtipo>/TEMPLATE.md` com:
   - Frontmatter YAML: `subtipo`, `variante`, `descricao`, `fonte_original` (lista dos DOCX usados), `variaveis_requeridas`, `variaveis_opcionais`, `timbrado`, `clausulas_incluidas` (nova chave — ver abaixo).
   - Corpo construído: cláusulas-padrão + invariantes locais + placeholders identificados na Fase 3.
2. Criar `02-BIBLIOTECA/peticoes/<subtipo>/placeholders.json` — metadados de cada placeholder (descrição, exemplo, obrigatório, tipo).
3. Criar `02-BIBLIOTECA/peticoes/<subtipo>/_corpus/` — cópia de segurança dos DOCX originais usados como fonte (separado de `_fonte-originais-perito/` só para rastrear quais foram efetivamente analisados).

**Decisão pendente sobre inclusão de cláusulas-padrão:**
Duas opções, escolher na próxima sessão:
- **Opção A — literal no TEMPLATE.md:** cláusulas copiadas inline. Prós: zero infra extra, funciona com motor atual. Contras: mudança na cláusula obriga regenerar todos templates.
- **Opção B — sintaxe de inclusão:** adicionar ao motor `{{#incluir:clausulas-padrao/endereçamento}}`. Prós: DRY de verdade. Contras: estender motor.

Recomendação: começar com A (mais simples) e migrar para B se o número de templates crescer além de 10.

---

## Fase 5 — VALIDAÇÃO

Para cada template montado:

1. **Teste com FICHA real** — pegar o próprio CNJ/dados das peças originais usadas como fonte e montar uma `FICHA.json` reconstituindo-os. Rodar motor. Comparar saída com a peça original (diff linha a linha).
2. **Meta:** saída idêntica aos DOCX originais (igual já acontece com aceite/agendamento) OU diferenças pontuais justificadas (ex: reordenação deliberada para melhor fluxo).
3. **Teste com FICHA nova** — pegar um processo real diferente em andamento → preencher FICHA → gerar peça. Revisar manualmente. Se necessário, ajustar template.

**Output:** entrada nova em `TESTE-LOG.md` com resultados. Só marca template como ativo após passar nos 2 testes.

---

## Fase 6 — CATÁLOGO das cláusulas-padrão reutilizáveis

Local: `02-BIBLIOTECA/clausulas-padrao/` (já existe — pastas vazias atuais: preambulo, qualificacao-perito, metodologia, fundamentacao-complexidade, nexo-causal, avaliacao-dano, fecho).

Criar nesta fase (a partir dos 3 DOCX que já temos + novos conforme chegarem):

| Cláusula | Texto (extraído dos 3 DOCX atuais) |
|---|---|
| `enderecamento/CLAUSULA.md` | `AO JUÍZO DA {{juizo.numero_vara}}ª VARA {{juizo.materias}} DA COMARCA DE {{juizo.comarca}} – {{juizo.uf}}` |
| `identificador-processo/CLAUSULA.md` | `Processo nº: {{processo.cnj}}` |
| `vocativo/CLAUSULA.md` | `Meritíssimo Juiz,` (presente no aceite simples; ausente no aceite condicionado e agendamento — marcar como opcional) |
| `fecho/CLAUSULA.md` | `Termos em que,\nPede deferimento.` |
| `assinatura/CLAUSULA.md` | 3 linhas: nome, função-CRM, filiação |
| `data-local/CLAUSULA.md` | `{{data.por_extenso}}, Governador Valadares - MG.` |

Cada arquivo tem frontmatter: `nome`, `obrigatoria_em`, `opcional_em`, `variaveis_usadas`, `fonte_verificada`.

**ESTAS 6 JÁ SÃO EXTRAÍVEIS HOJE** — texto veio dos 3 DOCX reais que você já enviou. Posso criar na próxima sessão sem esperar mais peças.

---

## Ordem operacional recomendada para a próxima sessão

1. **PRIMEIRO:** criar as 6 cláusulas-padrão da Fase 6 (Dr. Jesus já forneceu base para isso).
2. **SEGUNDO:** quando Dr. Jesus avisar que subiu documentos novos em `_fonte-originais-perito/`, listar o que chegou, executar Fase 2-5 por subtipo.
3. **REGRA DE OURO:** se faltar peça real do subtipo → **NÃO criar template**. Marcar como "aguardando peça" no `_INDICE.md`.

---

## Decisões pendentes do Dr. Jesus (registrar respostas antes de prosseguir)

- [ ] Opção A ou B para inclusão de cláusulas-padrão (Fase 4)?
- [ ] Quantidade mínima de peças por subtipo antes de criar template (1, 2 ou 3)?
- [ ] Cláusula `vocativo` (`Meritíssimo Juiz,`) é obrigatória em proposta de honorários também, ou só em aceite? (no aceite condicionado e agendamento atuais não tem — investigar nos próximos documentos).

---

## Artefatos INVENTADOS nesta sessão que precisam ser REFEITOS com peça real

Marcados com prefixo `INVENTADO-NAO-USAR-`:
- `02-BIBLIOTECA/peticoes/escusa/INVENTADO-NAO-USAR-TEMPLATE.md`
- `02-BIBLIOTECA/peticoes/proposta-honorarios/civel-dano-pessoal/INVENTADO-NAO-USAR-TEMPLATE.md`
- `05-AUTOMACOES/scripts/INVENTADA-NAO-USAR-FICHA-EXEMPLO-escusa.json`
- `05-AUTOMACOES/scripts/INVENTADA-NAO-USAR-FICHA-EXEMPLO-civel-simples.json`
- `05-AUTOMACOES/scripts/INVENTADA-NAO-USAR-FICHA-EXEMPLO-civel-complexo.json`

Quando peça real chegar: extrair pelo processo acima e DELETAR (com confirmação do usuário) os arquivos `INVENTADO-NAO-USAR-*`.
