---
titulo: "Processo de Triagem do Inbox"
bloco: "16_inbox"
tipo: "runbook"
nivel: "todos"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 5
---

# Processo de Triagem do Inbox

Fluxo simples em 4 estados. Executar em sessão dedicada semanal (sábado de manhã, 30-45 min) ou quando inbox passar de 15 itens.

## Estados

1. **Bruto** — acabou de entrar em `to_process/`, ainda não olhado.
2. **Classificado** — já triado, recebeu bloco-destino tentativo, aguarda promoção.
3. **Promovido** — virou artefato em bloco permanente (`05_`, `10_` etc.) ou foi integrado a artefato existente.
4. **Descartado** — sem valor. Move para `16_inbox/descartados/` com motivo em 1 linha.

## Fluxo

```
[capturar]
    ↓
16_inbox/to_process/ (bruto)
    ↓ triagem semanal
classifica tag + bloco
    ↓
16_inbox/classificados/  (aguardando janela para promover)
    ↓
promove (cria artefato no bloco ou edita existente)
    ↓
marca nota original como promovida (campo promovido_para: <path>)
arquiva em 16_inbox/processados/
```

## Regras de decisão

### Promover quando

- Conteúdo agrega a artefato existente (edita o artefato + referencia nota).
- Conteúdo merece artefato próprio ≥ 30 linhas justificadas.
- Tem fonte verificável.

### Descartar quando

- Duplicata de conteúdo já existente.
- Fonte não-verificável e tema marginal.
- Passou 14 dias e não ficou claro para que serve.

### Deixar em stand-by quando

- Precisa de pesquisa adicional (`[TODO/RESEARCH]`).
- Depende de evento externo (release, decisão, dado futuro).

## Ritual semanal (30 min, sábado)

1. Abrir `16_inbox/to_process/`.
2. Contar itens. Se > 20, limitar triagem aos 20 mais antigos.
3. Para cada nota:
   - Ler em 60s.
   - Decidir: promover agora, classificar para depois, ou descartar.
   - Se promover: editar artefato destino, atualizar campo `promovido_para` na nota, mover para `processados/`.
   - Se classificar: ajustar frontmatter, mover para `classificados/`.
   - Se descartar: adicionar motivo em 1 linha, mover para `descartados/`.
4. Fechar sessão com 0 a 3 itens restantes em `to_process/`. Mais do que isso = inbox bankruptcy na próxima semana.

## Métrica

- **Lead time de nota**: dias entre captura e promoção. Meta: < 14 dias.
- **Taxa de descarte**: %. Alta (>50%) é saudável — captura livre, triagem rigorosa.
- **Promovidos/mês**: sinal de conhecimento consolidado.

## Automação sugerida (futuro)

- Hook Obsidian ou script que lista notas em `to_process/` com idade > 14 dias.
- Relatório mensal: quantas promovidas, quais blocos cresceram mais.
- Integração com `~/stemmia-forense/automacoes/` para extrair insumos.

## Anti-padrões

- Triagem preguiçosa: "deixa aqui que depois eu vejo" indefinidamente.
- Promoção sem critério: virar qualquer nota bruta em artefato → polui a base.
- Descarte sem motivo: perde aprendizado sobre o que não importou.
- Triagem no mesmo momento da captura: quebra fluxo, mistura modos cognitivos.

## Referência cruzada

- `modelo_nota_bruta.md`
- `../raw_conversations/README_como_importar.md`
