# CONTEXTO-CONTINUACAO — Cole isto em nova sessão Claude Code

**Objetivo:** retomar o pipeline medidor de distâncias Maps em nova sessão, com cidades e/ou origem diferentes, disparando os 3 Agent Teams em paralelo sem intervenção humana.

---

## COPIE E COLE O BLOCO ABAIXO

```
Leia estes 4 arquivos na ordem e depois execute:

1. /Users/jesus/Desktop/STEMMIA Dexter/Maestro/playbooks/medidor-distancias-maps/README.md
2. /Users/jesus/Desktop/STEMMIA Dexter/Maestro/playbooks/medidor-distancias-maps/PIPELINE.md
3. /Users/jesus/Desktop/STEMMIA Dexter/Maestro/playbooks/medidor-distancias-maps/AGENT-TEAMS-PLAYBOOK.md
4. /Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/distancias-gv/distancias_gv_maps.py (se já existir)

## MEUS PARÂMETROS

- Origem: <COLE AQUI — ex: "Governador Valadares", "Belo Horizonte", "Juiz de Fora">
- UF origem: <COLE — ex: "MG">
- Lista de destinos: <COLE — caminho de CSV ou JSON, ou "todas as comarcas TJMG" ou "subseções JF" etc>
- Quantos destinos esperados: <N — para validação>
- Populacional UF: <sigla — default MG>
- Raio para filtro downstream: <km — ex: 200>

## EXECUÇÃO

Dispare os 3 Agent Teams em UMA mensagem (3 tool_calls paralelos):
- Time A general-purpose — Fases 0+1+2 medidor Maps (use os parâmetros acima)
- Time B general-purpose — Fase 4.1 download IBGE da UF populacional
- Time C Explore — Fase 3.1 auditoria do script antigo (se v1 ainda for suspeito)

Depois que os 3 voltarem:
- Valide outputs
- Execute Fases 3.2-3.4 e 4.2-4.3 sequencialmente
- Entregue no chat: caminhos dos arquivos + top-30 priorizado

Zero perguntas antes. Se faltar parâmetro, assuma default GV/MG/comarcas TJMG.
```

---

## Exemplos de configurações prontas

### A) Cidades subseções JF (26)
```yaml
Origem: "Governador Valadares"
UF origem: "MG"
Lista de destinos: ler /Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/guia-tjmg-classificador/data/trf6_subsecoes.json campo "_subsecoes_mg"
Quantos esperados: 26
Populacional UF: MG
Raio filtro: 300
```

### B) Cidades AJG (conforme FICHA.json dos processos)
```yaml
Origem: "Governador Valadares"
UF origem: "MG"
Lista de destinos: CSV manual com nomes das comarcas onde Dr. Jesus tem perícia AJG pendente
Quantos esperados: N (conforme CSV)
Raio filtro: 500
```

### C) Origem diferente (ex: BH como hub secundário)
```yaml
Origem: "Belo Horizonte"
UF origem: "MG"
Lista de destinos: todas as comarcas TJMG
Quantos esperados: 298
Populacional UF: MG
Raio filtro: 150
Nota adicional: renomear output de distancias_gv_v2 para distancias_bh.json
```

### D) Outro estado (ex: SP)
```yaml
Origem: "São Paulo"
UF origem: "SP"
Lista de destinos: CSV próprio com comarcas TJSP
Quantos esperados: N
Populacional UF: SP (prefixo IBGE 35)
Raio filtro: 200
```

---

## REGRAS INEGOCIÁVEIS (herda do CLAUDE.md global)

1. **Opus 4.7** (model = claude-opus-4-7). Nunca trocar sem ordem.
2. **Zero fricção.** Permissões Bash(*), Edit(*), Write(*). Sem perguntas.
3. **PYTHON-BASE falhas.json** sempre consultado antes de código de automação.
4. **Maestro R2:** código vai em PYTHON-BASE/ ou src/, **documentação** vai em Maestro/playbooks/.
5. **Crash-safe obrigatório.** Cache write+flush+fsync por item. Rerun retoma.
6. **Deadline 18h para envio de email é rígido** — se tempo apertar, cortar para top-30 raio 100km.

---

## TROUBLESHOOTING

| Sintoma | Causa provável | Mitigação |
|---|---|---|
| Fase 0: seletor não casa | Google mudou DOM | Ler HTML dump + screenshot em logs/, ajustar regex |
| Fase 1: km fora da faixa em âncora | URL encoding quebrado OU homônimo em outra UF | Verificar `,+UF,+Brazil` na URL, checar coords retornadas |
| Fase 2: captcha após N cidades | Anti-bot ativou | Reduzir para 1 page, delay 15-30s, trocar UA, retomar do cache |
| Fase 4: fuzzy match <95 em muitos casos | Normalização divergente IBGE × TJMG | Ajustar norm (remover "d'", "de", hifen) antes do match |
| Fase 4: score zerado | Pop=0 em cache | Rechecar filtro UF no download IBGE |

---

## Manutenção deste playbook

- Se uma fase ganhar nova heurística útil → atualizar `PIPELINE.md`.
- Se novo tipo de falha aparecer → adicionar linha em "TROUBLESHOOTING" + registrar em `PYTHON-BASE/03-FALHAS-SOLUCOES/casos-reais/REGISTRO.md`.
- Commit na branch atual do Maestro com mensagem `docs(playbook): <mudança>`.
