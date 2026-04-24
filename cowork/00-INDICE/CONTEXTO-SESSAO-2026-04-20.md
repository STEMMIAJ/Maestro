# CONTEXTO COMPLETO — Sessão 2026-04-20 (cowork/)

Documento de handoff. Ler na íntegra no início da próxima sessão para continuar sem perder nada.

---

## 1. Onde estamos no projeto

O Dr. Jesus está construindo um **escritório digital pericial** em `~/Desktop/STEMMIA Dexter/cowork/`. Objetivo: toda petição, laudo e resposta sai em 1 comando a partir de dados estruturados do processo (`FICHA.json` por caso), usando templates extraídos das peças reais do perito.

**Princípio não-negociável:** templates só são criados a partir de peças reais do Dr. Jesus. Foi violado na sessão de 2026-04-20 (inventei 2 templates — marcados e segregados). Nunca mais.

---

## 2. Estrutura atual do `cowork/`

```
cowork/
├── 00-INDICE/
│   ├── README.md
│   ├── PLANO-ACAO.md                     ← estado geral das fases 0-6
│   ├── PLANO-EXTRACAO-TEMPLATES.md       ← processo de extração (criado 2026-04-20)
│   ├── CONTEXTO-SESSAO-2026-04-20.md     ← este arquivo
│   └── REPLICABILIDADE.md
│
├── 01-CASOS-ATIVOS/
│   └── _TEMPLATE-CASO/                   ← molde para cada novo caso
│       ├── FICHA.json                    ← skeleton estruturado (criado hoje)
│       ├── README.md                     ← instruções (criado hoje)
│       └── 6 pastas: _dados, documentos-recebidos, exames, laudo, peticoes-geradas, revisao
│
├── 02-BIBLIOTECA/
│   ├── _INDICE.md                        ← taxonomia (11 subtipos petição / 6 classes honorários / 6 classes laudo / 3 respostas)
│   │
│   ├── peticoes/
│   │   ├── _corpus-estilo/               ← vazio ainda
│   │   ├── _fonte-originais-perito/      ← 3 DOCX reais do perito (aceite×2 + agendamento)
│   │   │
│   │   ├── aceite/                       ★ FUNCIONAL (2 templates reais)
│   │   │   ├── TEMPLATE.md
│   │   │   ├── TEMPLATE-condicionado.md
│   │   │   └── placeholders.json
│   │   │
│   │   ├── agendamento/                  ★ FUNCIONAL (1 template real)
│   │   │   └── TEMPLATE.md
│   │   │
│   │   ├── escusa/                       ⚠ INVENTADO-NAO-USAR-TEMPLATE.md
│   │   ├── proposta-honorarios/
│   │   │   ├── civel-dano-pessoal/       ⚠ INVENTADO-NAO-USAR-TEMPLATE.md
│   │   │   ├── erro-medico/              (vazio — aguardando peça)
│   │   │   ├── securitario/              (vazio)
│   │   │   ├── previdenciario/           (vazio)
│   │   │   ├── trabalhista/              (vazio)
│   │   │   └── dpvat/                    (vazio)
│   │   ├── esclarecimento/               (vazio)
│   │   ├── majoracao-honorarios/         (vazio)
│   │   ├── impugnacao-quesitos/          (vazio)
│   │   ├── complementar/                 (vazio)
│   │   └── mutirao/                      (vazio)
│   │
│   ├── laudos/{6 classes}/               (todas vazias)
│   ├── respostas/{3 tipos}/              (todas vazias)
│   ├── clausulas-padrao/                 ← EXTRAÍVEL AGORA (ver PLANO-EXTRACAO-TEMPLATES.md Fase 6)
│   │   ├── preambulo/
│   │   ├── qualificacao-perito/
│   │   ├── metodologia/
│   │   ├── fundamentacao-complexidade/
│   │   ├── nexo-causal/
│   │   ├── avaliacao-dano/
│   │   └── fecho/
│   ├── quesitos/{6 especialidades}/      (vazias)
│   └── jurisprudencia/{5 áreas}/         (vazias)
│
├── 03-IDENTIDADE/
│   ├── dados-profissionais.md            ← preenchido com dados reais (CPF/RG/RQE pendentes)
│   ├── estilo-redacao-extraido.md        ← 10 seções do estilo do perito
│   └── timbrado/
│       ├── timbrado-topo-pagina.png      ★ timbrado oficial (500×500, vai no topo da página Word)
│       └── timbrado-variante-alternativa.png
│
├── 04-PIPELINES/
│   └── blocos-tempo-cronometrados.md     ← blocos TDAH/autismo (triagem 25min etc.)
│
├── 05-AUTOMACOES/
│   └── scripts/
│       ├── aplicar_template.py           ★ MOTOR v0.2.0 (205 linhas, stdlib)
│       ├── FICHA-EXEMPLO.json            ← teste real (CNJ Mantena)
│       ├── TESTE-LOG.md                  ← log de bateria 6/6 OK
│       └── INVENTADA-NAO-USAR-FICHA-EXEMPLO-*.json (3 arquivos)
│
└── 06-APRENDIZADO/
    ├── ANALISE-BANCO-MODELOS.md          ← plano ultrathink 6 níveis, gatilho ≥30 peças
    └── IDEIA-proposta-honorarios-por-classe.md  ← ideia CFM/RQE anotada
```

---

## 3. O que o motor `aplicar_template.py v0.2.0` faz

**Input:** TEMPLATE.md + FICHA.json + (opcional) data.
**Output:** MD preenchido no stdout ou em arquivo.

**Sintaxes suportadas:**

| Sintaxe | O que faz |
|---|---|
| `{{a.b.c}}` | substitui por `ficha["a"]["b"]["c"]` (caminho em dot notation) |
| `{{#lista:path:prefixo="X":separador="Y"}}` | expande lista de valores com prefixo + separador |
| `{{#se:path}}texto{{/se}}` | texto só aparece se `path` é truthy (não None, não False, não "", não [], não {}, não 0) |
| `{{#se-nao:path}}texto{{/se-nao}}` | inverso do anterior |
| `{{data.por_extenso}}` | data de hoje em PT-BR (`20 de abril de 2026`) |

**Falhas:** placeholder ausente vira `[[FALTA:path]]` no output + aviso no stderr (não quebra execução). RC=0 quando sem problemas, RC=2 quando há avisos.

**Rastreabilidade:** todo MD gerado termina com comentário HTML:
```
<!-- gerado por aplicar_template.py v0.2.0 em 2026-04-20T20:19:27-0300 | template=<path> | ficha=<path> -->
```

**Frontmatter YAML:** removido automaticamente do TEMPLATE antes da substituição.

**CLI:**
```
python3 aplicar_template.py --template <path> --ficha <path> [--saida <path>] [--data "DD de MÊS de AAAA"] [--dry-run]
```

**Testes passados (2026-04-20):**
- 7 unitários do condicional (`_truthy`, multilinha, se/se-nao, combinação com placeholders simples)
- 3 regressões com templates reais (aceite, aceite-condicionado, agendamento) → saída IDÊNTICA aos DOCX originais
- 3 testes com templates/fichas inventados (agora marcados `INVENTADO-NAO-USAR-`)

---

## 4. Skill `/peticao` criada

Local: `~/.claude/skills/peticao-cowork/SKILL.md`

Dispara quando o usuário diz "faz petição de aceite pro caso X", "/peticao aceite", etc.
Passos: identifica tipo → localiza caso → valida FICHA → roda motor → verifica stderr → exibe MD.

Regras da skill: não inventar dados, UTF-8, EN DASH, output em `01-CASOS-ATIVOS/<CNJ>/peticoes-geradas/`.

---

## 5. O que o Dr. Jesus pediu agora (fim da sessão 2026-04-20)

> "Vou te mandar documentos reais meus. Extraí os templates a partir disso. Parte das petições se repete em todas — vamos definir num .md. Me dá o contexto inteiro para continuar em outra sessão sem perder nada."

### Ação derivada:
1. ✅ Criado `PLANO-EXTRACAO-TEMPLATES.md` (processo de 6 fases + cláusulas-padrão reutilizáveis).
2. ✅ Criado este `CONTEXTO-SESSAO-2026-04-20.md` para handoff.
3. ⏳ Aguardando Dr. Jesus subir peças em `02-BIBLIOTECA/peticoes/_fonte-originais-perito/<subtipo>/`.

---

## 6. Decisões pendentes (Dr. Jesus precisa responder)

1. **Inclusão de cláusulas-padrão:** opção A (literal inline no TEMPLATE) ou B (estender motor com `{{#incluir:}}`)?
2. **Quantidade mínima de peças por subtipo** antes de criar template: 1, 2 ou 3?
3. **Cláusula `vocativo` (`Meritíssimo Juiz,`):** obrigatória em proposta-honorarios também, ou só em aceite? (investigar quando chegarem peças novas)
4. **Dados ainda pendentes em `03-IDENTIDADE/dados-profissionais.md`:** CPF, RG, RQE, especialidade registrada, CEP, banco/PIX.

---

## 7. Próxima sessão — ordem operacional

1. **Ler este arquivo inteiro** (`CONTEXTO-SESSAO-2026-04-20.md`) + `PLANO-EXTRACAO-TEMPLATES.md`.
2. **Listar** `02-BIBLIOTECA/peticoes/_fonte-originais-perito/` para ver o que Dr. Jesus subiu.
3. **Executar Fase 6 do plano** (criar as 6 cláusulas-padrão a partir dos 3 DOCX já existentes) — NÃO depende de peça nova, pode ser a primeira coisa feita.
4. **Para cada nova pasta com peças reais:** executar Fases 2-5 do `PLANO-EXTRACAO-TEMPLATES.md`.
5. **Quando um novo template for verificado** (Fase 5), DELETAR o correspondente `INVENTADO-NAO-USAR-*` (com confirmação).

---

## 8. Comandos úteis para próxima sessão

```bash
# Ver estado geral
cat "/Users/jesus/Desktop/STEMMIA Dexter/cowork/00-INDICE/PLANO-ACAO.md"
cat "/Users/jesus/Desktop/STEMMIA Dexter/cowork/00-INDICE/PLANO-EXTRACAO-TEMPLATES.md"

# Ver o que chegou de novo
find "/Users/jesus/Desktop/STEMMIA Dexter/cowork/02-BIBLIOTECA/peticoes/_fonte-originais-perito/" -type f -newer "/Users/jesus/Desktop/STEMMIA Dexter/cowork/00-INDICE/CONTEXTO-SESSAO-2026-04-20.md"

# Testar motor rápido
python3 "/Users/jesus/Desktop/STEMMIA Dexter/cowork/05-AUTOMACOES/scripts/aplicar_template.py" \
  --template "/Users/jesus/Desktop/STEMMIA Dexter/cowork/02-BIBLIOTECA/peticoes/aceite/TEMPLATE.md" \
  --ficha   "/Users/jesus/Desktop/STEMMIA Dexter/cowork/05-AUTOMACOES/scripts/FICHA-EXEMPLO.json" \
  --dry-run

# Extrair texto de DOCX novo (quando chegarem)
python3 -m zipfile -e "arquivo.docx" /tmp/docx_extracted/
grep -oE "<w:t[^>]*>[^<]+</w:t>" /tmp/docx_extracted/word/document.xml | sed 's/<[^>]*>//g'
```

---

## 9. Artefatos que violaram a regra zero (segregados, não deletados)

Prefixo `INVENTADO-NAO-USAR-`:
- `02-BIBLIOTECA/peticoes/escusa/INVENTADO-NAO-USAR-TEMPLATE.md`
- `02-BIBLIOTECA/peticoes/proposta-honorarios/civel-dano-pessoal/INVENTADO-NAO-USAR-TEMPLATE.md`
- `05-AUTOMACOES/scripts/INVENTADA-NAO-USAR-FICHA-EXEMPLO-escusa.json`
- `05-AUTOMACOES/scripts/INVENTADA-NAO-USAR-FICHA-EXEMPLO-civel-simples.json`
- `05-AUTOMACOES/scripts/INVENTADA-NAO-USAR-FICHA-EXEMPLO-civel-complexo.json`

Mantidos apenas como lembrete do erro. Deletar após substituir por versão real.

---

## 10. Resumo em uma frase

Motor `aplicar_template.py v0.2.0` está funcional e testado (3 templates reais de aceite/agendamento geram saída idêntica aos DOCX originais); infra do escritório digital está de pé; próxima etapa é extrair templates dos DOCX que o Dr. Jesus está baixando agora, seguindo o processo de 6 fases do `PLANO-EXTRACAO-TEMPLATES.md`.
