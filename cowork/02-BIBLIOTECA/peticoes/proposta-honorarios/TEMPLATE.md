---
subtipo: proposta-honorarios
variante: avulsa
fonte_original: MODELOS PETIÇÕES PLACEHOLDERS/proposta/proposta-honorarios.md
duracao_bloco: 5min
quando_usar: Juiz pede proposta de honorários em petição separada do aceite (CPC 465 §2º I)
legislacao: CPC art. 465, §2º, I; Resolução CNJ nº 232/2016, art. 3º
variaveis_requeridas:
  - juizo.numero_vara            # ex: "2"
  - juizo.materias               # ex: "CÍVEL"
  - juizo.comarca                # ex: "GOVERNADOR VALADARES"
  - juizo.uf                     # ex: "MG"
  - juizo.vocativo               # ex: "Meritíssimo Juiz,"
  - processo.cnj                 # ex: "5008297-73.2025.8.13.0105"
  - processo.id_decisao          # ex: "10637932621"
  - honorarios.valor_numerico    # ex: "612,00"
  - honorarios.valor_extenso     # ex: "seiscentos e doze reais"
  - honorarios.fundamentacao     # ex: "Valor conforme Portaria TJMG 7231/2025..."
  - honorarios.faixa_tabela      # ex: "R$ 400,00 a R$ 3.060,00"
  - pericia.tipo                 # ex: "perícia médica cível"
  - data.por_extenso             # ex: "24 de abril de 2026"
variaveis_opcionais: []
timbrado:
  topo_pagina: ../../03-IDENTIDADE/timbrado/timbrado-topo-pagina.png
  rodape_texto: "Empresarial Maria Costa, Rua João Pinheiro, 531, Sala 207 – Centro – Governador Valadares/MG | (33) 99900-1122 | perito@drjesus.com.br"
---

AO JUÍZO DA {{juizo.numero_vara}}ª VARA {{juizo.materias}} DA COMARCA DE {{juizo.comarca}} – {{juizo.uf}}

Processo nº: {{processo.cnj}}

**MANIFESTAÇÃO – PROPOSTA DE HONORÁRIOS PERICIAIS**

{{juizo.vocativo}}

Em atenção à decisão de **ID {{processo.id_decisao}}**, venho, nos termos do art. 465, §2º, I, do CPC, apresentar proposta de honorários periciais.

**I — DO VALOR**

Proponho honorários periciais no valor de R$ {{honorarios.valor_numerico}} ({{honorarios.valor_extenso}}).

**II — FUNDAMENTAÇÃO**

{{honorarios.fundamentacao}}

**III — REFERÊNCIAS NORMATIVAS**

- Resolução CNJ nº 232/2016, art. 3º — parâmetros de remuneração pericial
- Tabela de Honorários Periciais do TJMG (Portaria 7231/2025) — faixa para {{pericia.tipo}}: {{honorarios.faixa_tabela}}

**IV — DADOS BANCÁRIOS**

Banco: Santander (033)
Agência: 2960 (Digital)
Conta Corrente: 01035135-5
PIX: perito@drjesus.com.br
Titular: Jesus Eduardo Noleto da Penha
CPF: 127.858.856-60

Requeiro a intimação das partes para manifestação sobre a proposta de honorários, no prazo legal.

Termos em que,
Pede deferimento.

Dr. Jésus Eduardo Nolêto da Penha
Médico – Perito Judicial – CRM-MG 92.148
Membro da ABMLPM – Associação Brasileira de Medicina Legal e Perícia Médica

{{data.por_extenso}}, Governador Valadares – MG.
