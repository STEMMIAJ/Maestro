---
titulo: "Modelo de Nota Bruta"
bloco: "16_inbox"
tipo: "template"
nivel: "todos"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 3
---

# Modelo de Nota Bruta

Usar este template para capturar qualquer ideia, link, dúvida ou trecho antes de classificar. Nota bruta entra em `16_inbox/to_process/` como arquivo individual.

## Regras

- Nome do arquivo: `AAAA-MM-DD_tema-curto.md` (sem acento, minúsculas, hífens).
- Conteúdo mínimo: fonte + resumo em 3 linhas + tag tentativa.
- Não revisar agora — captura bruta primeiro, triagem depois.
- Limite de vida útil: 14 dias no inbox. Depois, ou promove ou descarta.

## Template

```markdown
---
titulo: "[tema em 1 linha]"
bloco: "16_inbox"
tipo: "nota_bruta"
data_captura: AAAA-MM-DD
fonte: "[url / livro / conversa / intuição]"
tag_tentativa: "[ex: lgpd, python, perito, carreira, cloud]"
status: "bruto"
promovido_para: null
---

# [Título]

## Resumo (3 linhas)

...

## Trecho bruto / link

...

## Por que importa

...

## Ação sugerida

- [ ] Promover para bloco X
- [ ] Descartar
- [ ] Pesquisar mais antes de classificar
```

## Exemplo preenchido

```markdown
---
titulo: "ANPD publicou resolução sobre incidentes"
bloco: "16_inbox"
tipo: "nota_bruta"
data_captura: 2026-04-23
fonte: "https://www.gov.br/anpd/..."
tag_tentativa: "lgpd, incidente, prazo"
status: "bruto"
promovido_para: null
---

# ANPD publicou resolução sobre incidentes

## Resumo

Resolução CD/ANPD nº X/2026 atualiza prazo de comunicação para 3 dias
úteis e detalha conteúdo mínimo. Revoga normativo anterior.

## Trecho bruto / link

[copiar dispositivos relevantes ou link]

## Por que importa

Atualiza `05_security_and_governance/incident_response/comunicacao_ANPD_e_titular.md`
que está com [TODO/RESEARCH: prazos 2026].

## Ação sugerida

- [x] Promover para bloco 05, atualizar comunicacao_ANPD_e_titular.md
```

## Regra do "não deixa vazar"

Nota bruta nunca fica no Desktop, no e-mail como rascunho, ou em app externo — sempre vai direto para `16_inbox/to_process/`. Se capturou no celular, sincronizar via Obsidian ou transferir na próxima janela.

## Referência cruzada

- `processo_de_triagem.md`
- `../raw_conversations/README_como_importar.md`
