---
subtipo: aceite
variante: simples
fonte_original: _fonte-originais-perito/Aceite - 0038122-07.2012.8.13.0396 - Mantena.docx
duracao_bloco: 15min
variaveis_requeridas:
  - juizo.numero_vara            # ex: "2"
  - juizo.materias               # ex: "CÍVEL, CRIMINAL E DA INFÂNCIA E DA JUVENTUDE"
  - juizo.comarca                # ex: "MANTENA"
  - juizo.uf                     # ex: "MG"
  - processo.cnj                 # ex: "0038122-07.2012.8.13.0396"
  - atos_anteriores.ids          # lista. ex: ["10637932621","10639375978"]
  - data.por_extenso             # ex: "17 de março de 2026"
variaveis_opcionais: []
timbrado:
  topo_pagina: ../../03-IDENTIDADE/timbrado/timbrado-topo-pagina.png
  rodape_texto: "Empresarial Maria Costa, Rua João Pinheiro, 531, Sala 207 – Centro – Governador Valadares/MG | (33) 99900-1122 | perito@drjesus.com.br"
---

AO JUÍZO DA {{juizo.numero_vara}}ª VARA {{juizo.materias}} DA COMARCA DE {{juizo.comarca}} – {{juizo.uf}}

Processo nº: {{processo.cnj}}

MANIFESTAÇÃO – ACEITE DE ENCARGO E HONORÁRIOS

Meritíssimo Juiz,

Em atenção {{#lista:atos_anteriores.ids:prefixo="à(s) decisão/intimação de ID ":separador=" e ID "}}, venho ratificar meu aceite dos encargos e honorários periciais. Aguardo os trâmites necessários para prosseguir com o agendamento da perícia médica, caso não haja suspeição ou impedimento sobre minha atuação.

Termos em que,
Pede deferimento.

Dr. Jésus Eduardo Nolêto da Penha
Médico - Perito Judicial – CRM-MG 92.148
Membro da ABMLPM - Associação Brasileira de Medicina Legal e Perícia Médica

{{data.por_extenso}}, Governador Valadares - MG.
