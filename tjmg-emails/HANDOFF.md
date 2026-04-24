# HANDOFF — Extrator emails TJMG + Consultor proximidade GV
Data: 2026-04-24 06h45 | Modelo: Opus 4.7 | Sessão: ~30min, 2 agentes Opus paralelos

## 1. O QUE FOI FEITO (✅ DONE)

### Time A — Extrator profundo (`extrator_completo.py`)
- 1621/1621 PDFs do TJMG processados em **4,1s** (zero erros)
- **297/298 sedes com pelo menos 1 email** (99,7%)
- **1.038 emails únicos** extraídos (1.172 totais, com duplicatas entre setores)
- 96 emails (~8%) reconstruídos por inferência (sufixo `@tjmg.j*` → completar `tjmg.jus.br`) — flag `email_completado_inferencia: true` em cada
- Única sem email: **Abaeté** (PDF do TJMG informa "consulta sem resultado")

### Time B — Consultor proximidade (`comarcas_proximas_gv.py`)
- CLI com `--raio`, `--tipo`, `--entrancia`, `--com-email`, `--setor`, `--formato {tabela,csv,json,md,html}`, `--output`, `--limite`
- Cruza distâncias (já existiam em `distancias-gv/output/distancias_gv.json`) × contatos completos
- Match indireto via municípios subordinados quando sede não está nominalmente no JSON de distâncias

### Resultados por raio (todos com email)
| Raio | Comarcas |
|---|---|
| 50 km | 4 |
| 100 km | 13 |
| 200 km | 43 |

## 2. ARQUIVOS CRIADOS

```
/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/guia-tjmg-classificador/
├── extrator_completo.py                     (22 KB)
├── comarcas_proximas_gv.py
├── data/contatos_completo.json              (1,1 MB, 1616 entradas)
├── logs/extrator_completo.log               (7,5 KB)
├── logs/extrator_orfaos.json                (vazio = 0 erros)
└── output/
    ├── comarcas_50km.md                     (4)
    ├── comarcas_100km.md                    (13)
    ├── comarcas_100km.csv                   (pronto Excel/mailmerge)
    ├── comarcas_200km.md                    (43)
    └── comarcas_proximas.json               (26 KB)
```

## 3. SCHEMA `contatos_completo.json`

```json
{
  "Governador Valadares": {
    "codigo_tjmg": "0105",
    "tipo": "comarca|municipio|distrito",
    "forum_nome": "Doutor Joaquim de Assis Martins Costa",
    "endereco": {"logradouro","numero","bairro","cidade","uf","cep"},
    "telefone_principal": "(33) 3279-5800",
    "fax_principal": "...",
    "feriados_municipais": [...],
    "setores": [{"nome","sigla","andar","telefone","ramais","email","fax","email_completado_inferencia": false}],
    "varas": [{"nome","competencia","juiz_titular","telefone","email"}],
    "comarca_mae": "..." (só p/ municípios/distritos),
    "arquivo_origem": "Governador_Valadares.pdf",
    "paginas_processadas": 4,
    "extracao_timestamp": "2026-04-24T..."
  }
}
```

## 4. AMOSTRA — TOP 5 PRÓXIMAS DE GV (raio 100 km)

| # | km | Comarca | Email admin |
|---|---:|---|---|
| 1 | 0  | Governador Valadares | gvsadm@tjmg.jus.br |
| 2 | 27 | Conselheiro Pena | csnadm@tjmg.jus.br |
| 3 | 37 | Tarumirim | trm1secretaria@tjmg.jus.br |
| 4 | 41 | Itanhomi | inhadm@tjmg.jus.br |
| 5 | 55 | Peçanha | pnhadm@tjmg.jus.br |

## 5. O QUE O DR. JESUS VAI ENVIAR NA PRÓXIMA SESSÃO

Lista do **TJMG** e da **JF (Justiça Federal — TRF6 / Subseções de MG)** com algum tipo de complemento. Aguardar formato (PDF/CSV/lista direta no chat) antes de propor pipeline.

## 6. PRÓXIMOS PASSOS (na próxima sessão, em ordem)

1. **Receber e parsear a lista TJMG + JF** que o Dr. Jesus enviar — não criar nada antes de ver o formato
2. **Cruzar com `contatos_completo.json`** se for lista de comarcas
3. **Auditar os 96 emails inferidos** (script lista cada um com link `https://www.tjmg.jus.br/portal-tjmg/comarcas/` p/ confirmação)
4. **Popular as 25 subseções JF** ainda pendentes em `data/trf6_subsecoes.json` (handoff anterior já mencionava — só GV completa)
5. **Gerar template de email apresentação** com mailmerge jinja2 por comarca
6. **Limpar `_antigo_GLOSSARIO-*` e `_antigo_pesquisa/`** (precisa `LIMPAR-LIBERADO`)

## 7. COMO RETOMAR (cole na nova sessão)

```
Leia /Users/jesus/Desktop/_MESA/40-CLAUDE/handoffs/HANDOFF-TJMG-EXTRATOR-EMAILS-2026-04-24.md
inteiro. Estou com a lista do TJMG e JF para te enviar — vou colar agora. Quando eu colar,
parseie, cruze com contatos_completo.json (1,1 MB) e me devolva: o que da minha lista bate
com o que já tenho, o que falta, e plano para os faltantes. Zero perguntas antes de eu colar a lista.
```

## 8. COMANDOS RÁPIDOS DE VERIFICAÇÃO

```bash
cd "/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/guia-tjmg-classificador"

# Contar comarcas com email
python3 -c "import json; d=json.load(open('data/contatos_completo.json')); s=[k for k,v in d.items() if v.get('tipo')=='comarca' and any(x.get('email') for x in v.get('setores',[]))]; print(f'{len(s)} sedes com email')"

# Listar 96 inferidos (para auditoria)
python3 -c "import json; d=json.load(open('data/contatos_completo.json'));
for nome, dados in d.items():
    for s in dados.get('setores',[]):
        if s.get('email_completado_inferencia'): print(f'{nome} | {s[\"nome\"]} | {s[\"email\"]}')"

# Re-rodar consultor
python3 comarcas_proximas_gv.py --raio 100 --formato md --output output/comarcas_100km.md
```

## 9. DECISÕES TOMADAS (NÃO REVISITAR)

1. **Estratégia B (page.get_text("dict"))** falhou — PDF é gerado já truncado pelo TJMG. Adotamos **inferência por sufixo conhecido** + flag de auditoria. Funcionou em 96 casos.
2. **`distancias_gv.csv` não existe** — só `.json`. Time B adaptou.
3. **Match indireto via subordinados**: sem isso, raio 100 km mostrava só 1 comarca; com a correção, mostra 13.
4. **Não tocamos** em `classificar.py` (mantido intacto).
5. **Belo Horizonte tem caso especial**: sigla minúscula + domínio padrão quando o corte foi antes do `@`.

## 10. RISCOS / LIMITAÇÕES CONHECIDOS

- 96 emails inferidos podem dar bounce (~8% do total). Filtrar pela flag antes de envio em massa.
- TJMG pode ter alterado emails desde a captura dos PDFs (data dos PDFs = data do scraping anterior). Validar amostra antes de campanha.
- Juiz titular extraído da pág. 2+ — campo opcional, nem todos têm.

---

**Modelo:** Opus 4.7 | **Branch:** main | **Status:** ✅ DONE Fase 1+2 | **Aguardando:** lista TJMG+JF do Dr. Jesus
